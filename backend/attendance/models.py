from django.db import models
from accounts.models import User, Branch


class HouseTypes(models.TextChoices):
    ARAVALI = 'ARAVALI', 'ARAVALI'
    NILGIRI = 'NILGIRI', 'NILGIRI'
    SHIVALIK = 'SHIVALIK' 'SHIVALIK'
    UDAIGIRI = 'UDAIGIRI' 'UDAIGIRI'

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
    roll_number = models.IntegerField()
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    house = models.ForeignKey(Houses, on_delete=models.SET_NULL, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return f"{self.name} ({self.roll_number})"


class AttendanceTypes(models.TextChoices):
    PRESENT = 'PRESENT', 'PRESENT'
    ABSENT = 'ABSENT', 'ABSENT'
    ON_DUTY = 'ON_DUTY', 'ON_DUTY' 
    LEAVE = 'LEAVE', 'LEAVE'
    LEAVE_SW = 'LEAVE_SW', 'LEAVE_SW'


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    morning_attendance = models.CharField(
        max_length=100,
        null=True,
        choices=AttendanceTypes.choices
    )
    evening_class_attendance = models.CharField(
        max_length=100,
        null=True,
        choices=AttendanceTypes.choices
    )
    morning_pt_attendance = models.CharField(
        max_length=100,
        null=True,
        choices=AttendanceTypes.choices
    )
    games_attendance = models.CharField(
        max_length=100,
        null=True,
        choices=AttendanceTypes.choices
    )
    night_dorm_attendance = models.CharField(
        max_length=100,
        null=True,
        choices=AttendanceTypes.choices
    )

class Meta:
    unique_together = ('student', 'date')  # Prevent duplicate entries
    

