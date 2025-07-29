from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Classroom
from attendance.serializers import ClassroomSerializer

class ClassroomViewSet(viewsets.ModelViewSet):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer

# views.py
from rest_framework_simplejwt.views import TokenObtainPairView
from .serialiser import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
