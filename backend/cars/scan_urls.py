from django.urls import path
from .views import ScanView

urlpatterns = [
    path('<uuid:car_uuid>/', ScanView.as_view(), name='car-scan'),
]
