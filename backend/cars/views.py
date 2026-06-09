from django.http import HttpResponse
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .models import Car
from .serializers import CarSerializer, PublicCarSerializer
from .qr_utils import generate_qr_image, generate_qr_pdf


class CarListCreateView(generics.ListCreateAPIView):
    serializer_class = CarSerializer

    def get_queryset(self):
        return Car.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CarDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CarSerializer

    def get_queryset(self):
        return Car.objects.filter(owner=self.request.user)

    def get_object(self):
        try:
            return Car.objects.get(uuid=self.kwargs['uuid'], owner=self.request.user)
        except Car.DoesNotExist:
            raise NotFound()


class CarQRImageView(APIView):
    def get(self, request, uuid):
        try:
            car = Car.objects.get(uuid=uuid, owner=request.user)
        except Car.DoesNotExist:
            raise NotFound()
        png = generate_qr_image(car)
        return HttpResponse(png, content_type='image/png')


class CarQRPDFView(APIView):
    def get(self, request, uuid):
        try:
            car = Car.objects.get(uuid=uuid, owner=request.user)
        except Car.DoesNotExist:
            raise NotFound()
        pdf = generate_qr_pdf(car)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{car.plate_number}_qr.pdf"'
        return response


class ScanView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, car_uuid):
        try:
            car = Car.objects.get(uuid=car_uuid)
        except Car.DoesNotExist:
            raise NotFound()
        serializer = PublicCarSerializer(car)
        return Response(serializer.data)
