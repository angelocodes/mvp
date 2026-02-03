from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserListCreateView.as_view(), name='user-list-create'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('me/', views.current_user, name='current-user'),
    path('me/profile/', views.update_profile, name='update-profile'),
    path('me/password/', views.change_password, name='change-password'),
    path('me/stats/', views.get_user_stats, name='user-stats'),
    path('<int:pk>/profile/', views.update_profile, name='update-profile-admin'),
    path('<int:pk>/stats/', views.get_user_stats, name='user-stats-admin'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
]
