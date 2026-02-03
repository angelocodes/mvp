import json
from django.utils import timezone
from .models import AuditLog


class AuditLogger:
    """Utility class for creating audit log entries"""
    
    @staticmethod
    def log_action(user, action, object_type, object_id, details=None):
        """Create an audit log entry"""
        if not user or not user.is_authenticated:
            return None
            
        audit_entry = AuditLog.objects.create(
            user=user,
            action=action,
            object_type=object_type,
            object_id=object_id,
            details=json.dumps(details) if details else ''
        )
        return audit_entry
    
    @staticmethod
    def log_project_action(user, action, project, details=None):
        """Log a project-related action"""
        project_details = {
            'project_name': project.method_name,
            'project_status': project.status,
            **(details or {})
        }
        return AuditLogger.log_action(user, action, 'project', project.id, project_details)
    
    @staticmethod
    def log_user_action(user, action, target_user, details=None):
        """Log a user-related action"""
        user_details = {
            'target_username': target_user.username,
            'target_role': target_user.role,
            **(details or {})
        }
        return AuditLogger.log_action(user, action, 'user', target_user.id, user_details)
    
    @staticmethod
    def log_validation_action(user, action, project, validation_step, details=None):
        """Log a validation-related action"""
        validation_details = {
            'project_name': project.method_name,
            'validation_step': validation_step,
            **(details or {})
        }
        return AuditLogger.log_action(user, action, 'validation', project.id, validation_details)
    
    @staticmethod
    def log_auth_action(user, action, details=None):
        """Log authentication-related actions"""
        return AuditLogger.log_action(user, action, 'auth', user.id, details)
