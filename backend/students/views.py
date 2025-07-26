from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from attendance.models import Student
from .serializers import StudentSerializer
from rest_framework.permissions import IsAuthenticated

class StudentListCreateView(generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        class_name = self.request.query_params.get('class_name')
        if class_name:
            return self.queryset.filter(class_name=class_name)
        return self.queryset
