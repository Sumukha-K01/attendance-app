from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20)
    class_name = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name} - {self.class_name}"
