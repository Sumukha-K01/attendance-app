from django.db import models
from attendance.models import Student

class Exam(models.Model):
    """
    Model for storing exam/assessment information.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.name
    

class Results(models.Model):
    """
    Model for storing results of students.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='results')
    subject = models.CharField(max_length=100)
    score = models.IntegerField()
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_results')

    class Meta:
        unique_together = ('student', 'subject', 'exam')  # Ensure unique results per student, subject, and exam

    def __str__(self):
        return f"{self.student.name} - {self.subject} - {self.score} on {self.exam.name}"