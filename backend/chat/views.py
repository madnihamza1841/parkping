from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, PermissionDenied
from django.db import IntegrityError
from cars.models import Car
from .models import ChatThread, Message
from .serializers import ChatThreadSerializer, MessageSerializer


class StartChatView(APIView):
    def post(self, request, car_uuid):
        try:
            car = Car.objects.get(uuid=car_uuid)
        except Car.DoesNotExist:
            raise NotFound()

        if car.owner == request.user:
            return Response({'detail': 'Cannot chat with yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        thread, created = ChatThread.objects.get_or_create(scanner=request.user, car=car)
        serializer = ChatThreadSerializer(thread)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=status_code)


class ThreadListView(generics.ListAPIView):
    serializer_class = ChatThreadSerializer

    def get_queryset(self):
        user = self.request.user
        return ChatThread.objects.filter(
            scanner=user
        ) | ChatThread.objects.filter(car__owner=user)


class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer

    def get_thread(self):
        thread_id = self.kwargs['thread_id']
        user = self.request.user
        try:
            thread = ChatThread.objects.get(uuid=thread_id)
        except ChatThread.DoesNotExist:
            raise NotFound()
        if user != thread.scanner and user != thread.car.owner:
            raise PermissionDenied()
        return thread

    def get_queryset(self):
        return self.get_thread().messages.all()

    def perform_create(self, serializer):
        thread = self.get_thread()
        serializer.save(sender=self.request.user, thread=thread)
