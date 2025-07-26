from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from attendance.views import ClassroomViewSet, StudentViewSet, AttendanceViewSet


router = DefaultRouter()
router.register('classrooms', ClassroomViewSet)
router.register('students', StudentViewSet)
router.register('attendance', AttendanceViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),

    # JWT login endpoints
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Attendance app API
    path('api/', include(router.urls)),
]
