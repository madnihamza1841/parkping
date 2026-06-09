from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from cars.models import Car
from chat.models import ChatThread, Message
from .models import CallLog
from .agora_utils import generate_call_tokens, random_channel_id


def _send_incoming_call_push(owner, channel_id, token_b, car):
    """Send FCM push to car owner with call details."""
    try:
        from notifications.utils import send_push
        send_push(owner, 'Incoming call', f'Someone is calling about {car.nickname}', {
            'type': 'incoming_call',
            'channel_id': channel_id,
            'token': token_b,
            'car_nickname': car.nickname,
        })
    except Exception:
        pass


class CallTokenView(APIView):
    def post(self, request, car_uuid):
        try:
            car = Car.objects.get(uuid=car_uuid)
        except Car.DoesNotExist:
            raise NotFound()

        channel_id = random_channel_id()
        token_a, token_b = generate_call_tokens(channel_id)

        thread, _ = ChatThread.objects.get_or_create(scanner=request.user, car=car)

        call_log = CallLog.objects.create(
            channel_id=channel_id,
            initiated_by=request.user,
            car=car,
            thread=thread,
        )

        _send_incoming_call_push(car.owner, channel_id, token_b, car)

        return Response({
            'channel_id': channel_id,
            'token': token_a,
            'app_id': __import__('django.conf', fromlist=['settings']).settings.AGORA_APP_ID,
        }, status=status.HTTP_201_CREATED)


class CallStatusView(APIView):
    def post(self, request, channel_id):
        try:
            call = CallLog.objects.get(channel_id=channel_id)
        except CallLog.DoesNotExist:
            raise NotFound()

        new_status = request.data.get('status')
        valid = [s.value for s in CallLog.Status]
        if new_status not in valid:
            return Response({'detail': f'status must be one of {valid}'}, status=status.HTTP_400_BAD_REQUEST)

        call.status = new_status
        if new_status == 'ended' and 'duration_seconds' in request.data:
            call.duration_seconds = request.data['duration_seconds']
        call.save()

        # Insert system message for missed/declined calls
        if new_status in ('declined', 'missed') and call.thread:
            Message.objects.create(
                thread=call.thread,
                sender=None,
                content=f'Call {new_status}.',
                is_system=True,
            )

        return Response({'status': call.status})
