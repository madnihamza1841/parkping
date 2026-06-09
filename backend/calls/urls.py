from django.urls import path
from .views import CallTokenView, CallStatusView

urlpatterns = [
    path('token/<uuid:car_uuid>/', CallTokenView.as_view(), name='call-token'),
    path('status/<str:channel_id>/', CallStatusView.as_view(), name='call-status'),
]
