from django.urls import path, include

urlpatterns = [
    path('auth/login/', include('apps.users.urls')),
    path('auth/logout/', include('apps.users.urls')),
    path('users/', include('apps.users.urls')),
    path('projects/', include('apps.projects.urls')),
    path('projects/', include('apps.validation.urls')),
    path('projects/', include('apps.reports.urls')),
    path('audit/', include('apps.audit.urls')),
]
