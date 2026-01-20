from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserListCreateView.as_view(), name='user-list-create'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('me/', views.current_user, name='current-user'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
]
