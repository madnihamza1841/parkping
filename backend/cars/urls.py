from django.urls import path
from .views import CarListCreateView, CarDetailView, CarQRImageView, CarQRPDFView

urlpatterns = [
    path('', CarListCreateView.as_view(), name='car-list'),
    path('<uuid:uuid>/', CarDetailView.as_view(), name='car-detail'),
    path('<uuid:uuid>/qr/', CarQRImageView.as_view(), name='car-qr'),
    path('<uuid:uuid>/qr/pdf/', CarQRPDFView.as_view(), name='car-qr-pdf'),
]
