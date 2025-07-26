from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Classroom, Student, Attendance
from .serializers import ClassroomSerializer, StudentSerializer, AttendanceSerializer
from rest_framework.permissions import IsAuthenticated

class ClassroomViewSet(viewsets.ModelViewSet):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    @action(detail=True, methods=['get'], url_path='students')
    def students(self, request, id=None):
        classroom = self.get_object()
        students = Student.objects.filter(classroom=classroom)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    # Custom action to get attendance for a class on a specific date
    @action(detail=False, methods=['get'], url_path='by_class_date')
    def by_class_date(self, request):
        class_id = request.query_params.get('class_id')
        date = request.query_params.get('date')
        if not class_id or not date:
            return Response({'detail': 'class_id and date are required.'}, status=400)
        students = Student.objects.filter(classroom_id=class_id)
        attendance = Attendance.objects.filter(student__in=students, date=date)
        serializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data)
