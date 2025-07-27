from rest_framework import serializers
from .models import Classroom, Student, Attendance, Houses


class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ['id', 'name']

class StudentSerializer(serializers.ModelSerializer):
    classroom = serializers.PrimaryKeyRelatedField(queryset=Classroom.objects.all())

    class Meta:
        model = Student
        fields = '__all__'

# class AttendanceSerializer(serializers.ModelSerializer):
#     student_name = serializers.CharField(source='student.name', read_only=True)

#     class Meta:
#         model = Attendance
#         fields = ['id', 'student', 'student_name', 'date', 'status']


class HouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Houses
        fields = '__all__'


class AttendanceSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())

    class Meta:
        model = Attendance
        fields = ['student', 'date', 'morning_attendance', 'evening_class_attendance', 'morning_pt_attendance', 'games_attendance', 'night_dorm_attendance']
