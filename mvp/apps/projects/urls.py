from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.ProjectListCreateView.as_view(), name='project-list-create'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('<int:project_id>/workflow/', views.project_workflow, name='project-workflow'),
    path('<int:project_id>/start-validation/', views.start_validation, name='start-validation'),
    path('<int:project_id>/review/', views.review_project, name='review-project'),
    path('<int:project_id>/approve/', views.approve_project, name='approve-project'),
]
