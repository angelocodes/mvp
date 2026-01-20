from django.contrib import admin
from .models import AuditLog

class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'object_type', 'object_id')
    list_filter = ('action', 'object_type', 'timestamp')
    search_fields = ('user__username', 'details')
    readonly_fields = ('user', 'action', 'object_type', 'object_id', 'details', 'timestamp')
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

admin.site.register(AuditLog, AuditLogAdmin)
