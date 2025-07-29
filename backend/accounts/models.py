from django.contrib.auth.models import AbstractUser
from django.db import models

class Branch(models.Model):
    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        unique_together = ('branch', 'role')  # Only one admin and one superadmin per branch
class Classroom(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name