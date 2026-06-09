from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import DeviceToken


class RegisterDeviceView(APIView):
    def post(self, request):
        token = request.data.get('token')
        platform = request.data.get('platform')

        if not token or not platform:
            return Response({'detail': 'token and platform are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if platform not in [p.value for p in DeviceToken.Platform]:
            return Response({'detail': f'platform must be one of {[p.value for p in DeviceToken.Platform]}'}, status=status.HTTP_400_BAD_REQUEST)

        DeviceToken.objects.update_or_create(
            token=token,
            defaults={'user': request.user, 'platform': platform},
        )
        return Response({'detail': 'Device registered.'}, status=status.HTTP_200_OK)
