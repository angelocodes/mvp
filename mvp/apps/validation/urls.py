from django.urls import path
from . import views

urlpatterns = [
    path('projects/<int:project_id>/linearity/', views.linearity_view, name='linearity'),
    path('projects/<int:project_id>/accuracy/', views.accuracy_view, name='accuracy'),
    path('projects/<int:project_id>/precision/', views.precision_view, name='precision'),
    path('projects/<int:project_id>/lod-loq/', views.lod_loq_view, name='lod-loq'),
    path('projects/<int:project_id>/documents/', views.supporting_documents_view, name='documents'),
    path('projects/<int:project_id>/documents/<int:document_id>/download/', views.download_document, name='download_document'),
    path('projects/<int:project_id>/documents/<int:document_id>/', views.delete_document, name='delete_document'),
    path('projects/<int:project_id>/summary/', views.validation_summary_view, name='validation_summary'),
    path('projects/<int:project_id>/review/', views.submit_review_view, name='submit_review'),
]
