from django.urls import path
from . import views

app_name = 'validation'

urlpatterns = [
    path('<int:project_id>/linearity/', views.linearity_view, name='linearity'),
    path('<int:project_id>/accuracy/', views.accuracy_view, name='accuracy'),
    path('<int:project_id>/precision/', views.submit_precision, name='submit-precision'),
    path('<int:project_id>/precision/', views.get_precision, name='get-precision'),
    path('<int:project_id>/lod-loq/', views.submit_lod_loq, name='submit-lod-loq'),
    path('<int:project_id>/lod-loq/', views.get_lod_loq, name='get-lod-loq'),
]
