from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'action', 'action_display', 'object_type', 'object_id', 'details', 'timestamp']
