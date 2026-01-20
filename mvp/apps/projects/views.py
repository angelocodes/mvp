from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Project
from .serializers import ProjectSerializer, ProjectCreateSerializer
from apps.users.permissions import IsAnalystOrHigher, IsReviewerOrHigher, IsQAAdmin


class ProjectListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAnalystOrHigher]

    def get_queryset(self):
        # For MVP, users can see projects they created or have access to
        # For simplicity, all projects if analyst or higher
        # Order by most recent first
        return Project.objects.all().order_by('-created_at')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProjectCreateSerializer
        return ProjectSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsAnalystOrHigher]


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAnalystOrHigher])
def project_workflow(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    # Mock workflow data
    workflow = {
        'current_step': project.status,
        'allowed_next_actions': [],  # TODO: implement workflow logic
        'locked_steps': [],  # TODO
    }
    return Response(workflow)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAnalystOrHigher])
def start_validation(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.status != 'draft':
        return Response({'error': 'Validation already started'}, status=status.HTTP_400_BAD_REQUEST)
    project.status = 'linearity'
    project.save()
    return Response({'message': 'Validation started', 'status': project.status})


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsReviewerOrHigher])
def review_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.status != 'review':
        return Response({'error': 'Project not ready for review'}, status=status.HTTP_400_BAD_REQUEST)

    comment = request.data.get('comment', '')
    project.reviewer = request.user
    project.reviewer_comment = comment
    project.reviewed_at = timezone.now()
    project.save()
    return Response({'message': 'Project reviewed'})


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsQAAdmin])
def approve_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.status != 'review' or not project.reviewer:
        return Response({'error': 'Project not reviewed yet'}, status=status.HTTP_400_BAD_REQUEST)

    project.qa_approver = request.user
    project.approved_at = timezone.now()
    project.status = 'approved'
    project.save()
    return Response({'message': 'Project approved', 'status': project.status})
