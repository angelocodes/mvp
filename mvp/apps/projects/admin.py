from django.contrib import admin
from .models import Project

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('method_name', 'product_name', 'technique', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'technique', 'created_at')
    search_fields = ('method_name', 'product_name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('method_name', 'method_type', 'technique', 'guideline', 'product_name')
        }),
        ('Status & Workflow', {
            'fields': ('status', 'created_by')
        }),
        ('Review', {
            'fields': ('reviewer', 'reviewer_comment', 'reviewed_at')
        }),
        ('Approval', {
            'fields': ('qa_approver', 'approved_at', 'report_generated')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

admin.site.register(Project, ProjectAdmin)
