from django.urls import path
from .views import (
    AttendanceAPIView,
    DashboardAPIView,
    AllStudentAttendanceAPIView,
    StudentAPIView,
    BulkAddStudentsAPIView,
    SavePushSubscriptionAPIView,
    TriggerUnmarkedPushAPIView,
    UnsubscribePushAPIView,
)
urlpatterns = [
    # Other paths ...
    path('', AttendanceAPIView.as_view(), name='attendance-api'),
    path('dashboard/', DashboardAPIView.as_view(), name='attendance-dashboard'),
    path('get-all-attendance/', AllStudentAttendanceAPIView.as_view(), name='all-student-attendance'),
    path('students/', StudentAPIView.as_view(), name='student-attendance'),
    path('students/<int:student_id>/', StudentAPIView.as_view(), name='student-attendance-detail'),
    path('students/bulk-add/', BulkAddStudentsAPIView.as_view(), name='bulk-add-students'),
    path('push/subscribe/', SavePushSubscriptionAPIView.as_view(), name='push-subscribe'),
    path('push/trigger-unmarked/', TriggerUnmarkedPushAPIView.as_view(), name='push-trigger-unmarked'),
    path('push/unsubscribe/', UnsubscribePushAPIView.as_view(), name='push-unsubscribe'),
]
