from django.urls import path
from . import views

app_name = 'audit'

urlpatterns = [
    path('', views.AuditLogListView.as_view(), name='audit-list'),
    path('<int:project_id>/', views.ProjectAuditLogListView.as_view(), name='project-audit-list'),
]
