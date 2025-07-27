from django.urls import path
from .views import AttendanceAPIView

urlpatterns = [
    # Other paths ...
    path('', AttendanceAPIView.as_view(), name='attendance-api'),
]
