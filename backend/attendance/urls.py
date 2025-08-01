from django.urls import path
from .views import AttendanceAPIView, DashboardAPIView, AllStudentAttendanceAPIView

urlpatterns = [
    # Other paths ...
    path('', AttendanceAPIView.as_view(), name='attendance-api'),
    path('dashboard/', DashboardAPIView.as_view(), name='attendance-dashboard'),
    path('get-all-attendance/', AllStudentAttendanceAPIView.as_view(), name='all-student-attendance'),
]
