from django.db import models
from accounts.models import User, Branch


class HouseTypes(models.TextChoices):
    ARAVALI_SR = 'ARAVALI_SR', 'aravali_sr'
    NILGIRI_SR = 'NILGIRI_SR', 'nilgiri_sr'
    SHIVALIK_SR = 'SHIVALIK_SR','shivalik_sr'
    UDAIGIRI_SR = 'UDAIGIRI_SR', 'udaigiri_sr'
    ARAVALI_JR = 'ARAVALI_JR', 'aravali_jr'
    NILGIRI_JR = 'NILGIRI_JR', 'nilgiri_jr'
    SHIVALIK_JR = 'SHIVALIK_JR','shivalik_jr'
    UDAIGIRI_JR = 'UDAIGIRI_JR', 'udaigiri_jr'

class Houses(models.Model):
    """
    Model for static House names
    """

    name = models.CharField(
        max_length=100, null=False,
        choices=HouseTypes.choices
    )
class Classroom(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_number = models.IntegerField(db_index=True)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, db_index=True)
    house = models.ForeignKey(Houses, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    course = models.CharField(default='NA', max_length=100, null=True, blank=True)
    def __str__(self):
        return f"{self.name} ({self.roll_number})"
    class Meta:
        unique_together = ('roll_number', 'classroom', 'branch')  # Ensure unique roll number per classroom and branch

class AttendanceTypes(models.TextChoices):
    PRESENT = 'PRESENT', 'present'
    ABSENT = 'ABSENT', 'absent'
    ON_DUTY = 'ON_DUTY', 'on_duty' 
    LEAVE = 'LEAVE', 'leave'
    LEAVE_SW = 'LEAVE_SW', 'leave_sw'
    NOT_MARKED = 'NOT_MARKED', 'not_marked'


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_attendance', db_index=True)
    date = models.DateField(db_index=True)
    morning_attendance = models.CharField(
        max_length=100,
        null=True,
        choices=AttendanceTypes.choices,
        default=AttendanceTypes.NOT_MARKED
    )
    evening_class_attendance = models.CharField(
        max_length=100,
        null=True,
        choices=AttendanceTypes.choices,
        default=AttendanceTypes.NOT_MARKED
    )
    morning_pt_attendance = models.CharField(
        max_length=100,
        null=True,
        choices=AttendanceTypes.choices,
        default=AttendanceTypes.NOT_MARKED
    )
    games_attendance = models.CharField(
        max_length=100,
        null=True,
        choices=AttendanceTypes.choices,
        default=AttendanceTypes.NOT_MARKED
    )
    night_dorm_attendance = models.CharField(
        max_length=100,
        null=True,
        choices=AttendanceTypes.choices,
        default=AttendanceTypes.NOT_MARKED
    )

class Meta:
    unique_together = ('student', 'date')  # Prevent duplicate entries
    

