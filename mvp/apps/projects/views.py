from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Project
from .serializers import ProjectSerializer, ProjectCreateSerializer
from apps.users.permissions import IsAnalystOrHigher, IsReviewerOrHigher, IsQAAdmin
from apps.audit.utils import AuditLogger


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
        project = serializer.save(created_by=self.request.user)
        AuditLogger.log_project_action(
            self.request.user,
            'create',
            project,
            {'method_name': project.method_name, 'technique': project.technique}
        )


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsAnalystOrHigher]


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAnalystOrHigher])
def project_workflow(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Define workflow steps and their order
    workflow_steps = ['draft', 'linearity', 'accuracy', 'precision', 'lod_loq', 'review', 'approved']
    validation_steps = ['linearity', 'accuracy', 'precision', 'lod_loq']
    
    current_index = workflow_steps.index(project.status)
    
    # Determine allowed actions based on current status and user role
    allowed_actions = []
    locked_steps = []
    
    if project.status == 'draft':
        allowed_actions = ['start_validation']
        locked_steps = validation_steps + ['review', 'approved']
    elif project.status in validation_steps:
        allowed_actions = ['submit_validation_data']
        # Lock steps before current
        locked_steps = workflow_steps[:current_index]
        # Lock steps after review
        locked_steps.extend(['review', 'approved'])
    elif project.status == 'review':
        if request.user.role in ['reviewer', 'qa']:
            allowed_actions = ['review_project']
        locked_steps = workflow_steps[:current_index] + ['approved']
    elif project.status == 'approved':
        if request.user.role == 'qa':
            allowed_actions = ['generate_report', 'view_audit_log']
        locked_steps = workflow_steps[:current_index]
    
    workflow = {
        'current_step': project.status,
        'current_step_index': current_index,
        'total_steps': len(workflow_steps),
        'allowed_next_actions': allowed_actions,
        'locked_steps': locked_steps,
        'workflow_steps': workflow_steps,
        'validation_steps': validation_steps,
        'can_edit': project.status not in ['review', 'approved'],
        'is_locked': project.status == 'approved',
        'reviewer_assigned': project.reviewer is not None,
        'qa_approver_assigned': project.qa_approver is not None,
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
    AuditLogger.log_project_action(
        request.user,
        'submit',
        project,
        {'action': 'started_validation', 'previous_status': 'draft', 'new_status': 'linearity'}
    )
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
    AuditLogger.log_project_action(
        request.user,
        'review',
        project,
        {'reviewer_comment': comment, 'reviewed_at': str(timezone.now())}
    )
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
    AuditLogger.log_project_action(
        request.user,
        'approve',
        project,
        {'qa_approver': request.user.username, 'approved_at': str(timezone.now())}
    )
    return Response({'message': 'Project approved', 'status': project.status})
