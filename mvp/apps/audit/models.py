from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('submit', 'Submit'),
        ('review', 'Review'),
        ('approve', 'Approve'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    object_type = models.CharField(max_length=50)  # e.g. 'project', 'user'
    object_id = models.PositiveIntegerField()
    details = models.TextField(blank=True)  # JSON or text details
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} {self.action} {self.object_type} {self.object_id} at {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']
