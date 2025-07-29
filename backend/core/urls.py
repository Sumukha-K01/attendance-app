from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from attendance.views import ClassroomViewSet, StudentViewSet, AttendanceViewSet, HouseViewSet, AttendanceAPIView
from accounts.views import CustomTokenObtainPairView

router = DefaultRouter()
router.register('classrooms', ClassroomViewSet)
router.register('students', StudentViewSet)
# router.register('attendance', AttendanceAPIView, basename='attendance')
router.register('houses', HouseViewSet)  # Registering HouseViewSet

urlpatterns = [
    path('admin/', admin.site.urls),

    # JWT login endpoints
    path('api/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Attendance app API
    path('api/attendance/', include('attendance.urls')),  # Include attendance app URLs
    path('api/', include(router.urls)),
]
