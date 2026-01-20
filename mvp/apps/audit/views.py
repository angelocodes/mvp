from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import AuditLog
from .serializers import AuditLogSerializer
from apps.users.permissions import IsQAAdmin


class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsQAAdmin]

    def get_queryset(self):
        return AuditLog.objects.all()


class ProjectAuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsQAAdmin]

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return AuditLog.objects.filter(object_type='project', object_id=project_id)
