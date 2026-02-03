from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import AuditLog
from .serializers import AuditLogSerializer
from apps.users.permissions import IsQAAdmin


class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        # Get query parameters
        user_id = self.request.query_params.get('user_id')
        
        # QA can see all logs or filter by specific user
        if user.role == 'qa':
            if user_id:
                return AuditLog.objects.filter(user_id=user_id)
            return AuditLog.objects.all()
        
        # Regular users can only see their own logs
        return AuditLog.objects.filter(user=user)


class ProjectAuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsQAAdmin]

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return AuditLog.objects.filter(object_type='project', object_id=project_id)
