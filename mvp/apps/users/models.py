from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('analyst', 'Analyst'),
        ('reviewer', 'Reviewer'),
        ('qa', 'QA'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='analyst')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
