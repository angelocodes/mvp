from django.urls import path, include

urlpatterns = [
    path('auth/', include('apps.users.urls')),
    path('users/', include('apps.users.urls')),
    path('projects/', include('apps.projects.urls')),
    path('validation/', include('apps.validation.urls')),
    path('reports/', include('apps.reports.urls')),
    path('audit/', include('apps.audit.urls')),
]
