from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('<int:project_id>/', views.report_view, name='report'),
]
