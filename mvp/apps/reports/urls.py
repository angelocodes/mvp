from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('<int:project_id>/report/', views.report_view, name='report'),
]
