from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('projects/', views.projects, name='projects'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('re-analysis/', views.re_analysis, name='re_analysis'),
    path('review/', views.review, name='review'),
    path('admin/', views.admin, name='admin'),
]
