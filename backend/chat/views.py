from datetime import timedelta
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, PermissionDenied
from django.db.models import Q, Max, F
from django.db.models.functions import Coalesce, Greatest
from django.utils import timezone
from cars.models import Car
from .models import ChatThread, Message, Block, CHAT_EXPIRY
from .serializers import ChatThreadSerializer, MessageSerializer


def _expiry_cutoff():
    return timezone.now() - CHAT_EXPIRY


def get_thread_for_user(thread_id, user):
    """Fetch a thread and verify the user is a participant. 404/403 otherwise."""
    try:
        thread = ChatThread.objects.select_related('car__owner').get(uuid=thread_id)
    except ChatThread.DoesNotExist:
        raise NotFound()
    if user != thread.scanner and user != thread.car.owner:
        raise PermissionDenied()
    return thread


class StartChatView(APIView):
    def post(self, request, car_uuid):
        try:
            car = Car.objects.select_related('owner').get(uuid=car_uuid)
        except Car.DoesNotExist:
            raise NotFound()

        if car.owner == request.user:
            return Response({'detail': 'Cannot chat with yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        if Block.exists_between(request.user, car.owner):
            return Response({'detail': 'You cannot contact this user.'}, status=status.HTTP_403_FORBIDDEN)

        thread, created = ChatThread.objects.get_or_create(scanner=request.user, car=car)
        serializer = ChatThreadSerializer(thread, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class ThreadListView(generics.ListAPIView):
    serializer_class = ChatThreadSerializer

    def get_queryset(self):
        user = self.request.user
        cutoff = _expiry_cutoff()
        # A thread is visible until 24h after its last message
        # (or 24h after creation if no message was ever sent).
        return (
            ChatThread.objects
            .filter(Q(scanner=user) | Q(car__owner=user))
            .annotate(last_activity=Greatest(Coalesce(Max('messages__timestamp'), F('created_at')), F('created_at')))
            .filter(last_activity__gte=cutoff)
            .select_related('car__owner', 'scanner')
        )


class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer

    def get_thread(self):
        return get_thread_for_user(self.kwargs['thread_id'], self.request.user)

    def get_queryset(self):
        # Messages disappear 24 hours after being sent.
        return self.get_thread().messages.filter(timestamp__gte=_expiry_cutoff())

    def perform_create(self, serializer):
        thread = self.get_thread()
        other = thread.other_participant(self.request.user)
        if Block.exists_between(self.request.user, other):
            raise PermissionDenied('You cannot contact this user.')
        serializer.save(sender=self.request.user, thread=thread)


class BlockView(APIView):
    """Block the other participant of a thread.

    Operates on a thread so the client never needs (or learns) the other
    user's identity.
    """

    def post(self, request, thread_id):
        thread = get_thread_for_user(thread_id, request.user)
        other = thread.other_participant(request.user)
        Block.objects.get_or_create(blocker=request.user, blocked=other)
        return Response({'detail': 'User blocked.'}, status=status.HTTP_200_OK)


class UnblockView(APIView):
    def post(self, request, thread_id):
        thread = get_thread_for_user(thread_id, request.user)
        other = thread.other_participant(request.user)
        Block.objects.filter(blocker=request.user, blocked=other).delete()
        return Response({'detail': 'User unblocked.'}, status=status.HTTP_200_OK)
