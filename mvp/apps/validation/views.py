from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from django.utils import timezone
from apps.projects.models import Project
from apps.users.permissions import IsAnalystOrHigher
from apps.audit.utils import AuditLogger
from apps.users.permissions import IsReviewerOrHigher
from .models import ValidationStep, LinearityData, AccuracyData, PrecisionData, LODLOQData, SupportingDocument, ParameterReview
from .serializers import (
    LinearityDataSerializer, LinearitySubmitSerializer,
    AccuracyDataSerializer, AccuracySubmitSerializer,
    PrecisionDataSerializer, PrecisionSubmitSerializer,
    LODLOQDataSerializer, LODLOQSubmitSerializer
)
from .rules.linearity import evaluate_linearity
from .rules.accuracy import evaluate_accuracy
from .rules.precision import evaluate_precision
from .rules.lod_loq import evaluate_lod_loq
from .workflow import advance_workflow


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsAnalystOrHigher])
def linearity_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        # Check if already submitted
        if ValidationStep.objects.filter(project=project, step='linearity').exists():
            return Response({'error': 'Linearity data already submitted'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = LinearitySubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Evaluate
        result = evaluate_linearity(
            serializer.validated_data['concentrations'],
            serializer.validated_data['responses']
        )

        # Create validation step
        step = ValidationStep.objects.create(
            project=project,
            step='linearity',
            completed=True,
            passed=result['status'] == 'PASS'
        )

        # Create data record
        data = LinearityData.objects.create(
            validation_step=step,
            concentrations=serializer.validated_data['concentrations'],
            responses=serializer.validated_data['responses'],
            slope=result['metrics'].get('slope'),
            intercept=result['metrics'].get('intercept'),
            r_squared=result['metrics'].get('r_squared'),
            passed=step.passed
        )

        # Advance workflow
        old_status = project.status
        advance_workflow(project, 'linearity', step.passed)
        
        # Log the validation action
        AuditLogger.log_validation_action(
            request.user,
            'submit',
            project,
            'linearity',
            {
                'result': result['status'],
                'r_squared': result['metrics'].get('r_squared'),
                'previous_project_status': old_status,
                'new_project_status': project.status
            }
        )

        response_data = {
            'status': result['status'],
            'metrics': result['metrics'],
            'justification': result['justification']
        }

        return Response(response_data)

    else:  # GET
        step = ValidationStep.objects.filter(project=project, step='linearity').first()
        if not step:
            return Response({'error': 'Linearity data not found'}, status=status.HTTP_404_NOT_FOUND)

        data = LinearityData.objects.get(validation_step=step)
        serializer = LinearityDataSerializer(data)
        return Response(serializer.data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsAnalystOrHigher])
def accuracy_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        if ValidationStep.objects.filter(project=project, step='accuracy').exists():
            return Response({'error': 'Accuracy data already submitted'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AccuracySubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Evaluate
        result = evaluate_accuracy(
            serializer.validated_data['level'],
            serializer.validated_data['measured_values']
        )

        # Create records
        step = ValidationStep.objects.create(
            project=project,
            step='accuracy',
            completed=True,
            passed=result['status'] == 'PASS'
        )

        data = AccuracyData.objects.create(
            validation_step=step,
            level=serializer.validated_data['level'],
            measured_values=serializer.validated_data['measured_values'],
            mean_recovery=result['metrics'].get('mean_recovery'),
            rsd=result['metrics'].get('rsd'),
            passed=step.passed
        )

        old_status = project.status
        advance_workflow(project, 'accuracy', step.passed)
        
        # Log the validation action
        AuditLogger.log_validation_action(
            request.user,
            'submit',
            project,
            'accuracy',
            {
                'result': result['status'],
                'level': serializer.validated_data['level'],
                'mean_recovery': result['metrics'].get('mean_recovery'),
                'previous_project_status': old_status,
                'new_project_status': project.status
            }
        )

        response_data = {
            'status': result['status'],
            'metrics': result['metrics'],
            'justification': result['justification']
        }

        return Response(response_data)

    else:  # GET
        step = ValidationStep.objects.filter(project=project, step='accuracy').first()
        if not step:
            return Response({'error': 'Accuracy data not found'}, status=status.HTTP_404_NOT_FOUND)

        data = AccuracyData.objects.get(validation_step=step)
        serializer = AccuracyDataSerializer(data)
        return Response(serializer.data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsAnalystOrHigher])
def precision_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        if ValidationStep.objects.filter(project=project, step='precision').exists():
            return Response({'error': 'Precision data already submitted'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PrecisionSubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Evaluate
        result = evaluate_precision(serializer.validated_data['replicate_values'])

        # Create records
        step = ValidationStep.objects.create(
            project=project,
            step='precision',
            completed=True,
            passed=result['status'] == 'PASS'
        )

        data = PrecisionData.objects.create(
            validation_step=step,
            replicate_values=serializer.validated_data['replicate_values'],
            mean=result['metrics'].get('mean'),
            rsd=result['metrics'].get('rsd'),
            passed=step.passed
        )

        old_status = project.status
        advance_workflow(project, 'precision', step.passed)
        
        # Log the validation action
        AuditLogger.log_validation_action(
            request.user,
            'submit',
            project,
            'precision',
            {
                'result': result['status'],
                'rsd': result['metrics'].get('rsd'),
                'mean': result['metrics'].get('mean'),
                'previous_project_status': old_status,
                'new_project_status': project.status
            }
        )

        response_data = {
            'status': result['status'],
            'metrics': result['metrics'],
            'justification': result['justification']
        }

        return Response(response_data)

    else:  # GET
        step = ValidationStep.objects.filter(project=project, step='precision').first()
        if not step:
            return Response({'error': 'Precision data not found'}, status=status.HTTP_404_NOT_FOUND)

        data = PrecisionData.objects.get(validation_step=step)
        serializer = PrecisionDataSerializer(data)
        return Response(serializer.data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsAnalystOrHigher])
def lod_loq_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        if ValidationStep.objects.filter(project=project, step='lod_loq').exists():
            return Response({'error': 'LOD/LOQ data already submitted'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = LODLOQSubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Get slope from linearity
        linearity_step = ValidationStep.objects.filter(project=project, step='linearity').first()
        if not linearity_step or not linearity_step.passed:
            return Response({'error': 'Linearity must be completed and passed first'}, status=status.HTTP_400_BAD_REQUEST)

        linearity_data = LinearityData.objects.get(validation_step=linearity_step)
        slope = linearity_data.slope

        # Evaluate
        result = evaluate_lod_loq(
            serializer.validated_data['blank_responses'],
            slope
        )

        # Create records
        step = ValidationStep.objects.create(
            project=project,
            step='lod_loq',
            completed=True,
            passed=result['status'] == 'PASS'
        )

        data = LODLOQData.objects.create(
            validation_step=step,
            blank_responses=serializer.validated_data['blank_responses'],
            slope=slope,
            lod=result['metrics'].get('lod'),
            loq=result['metrics'].get('loq'),
            passed=step.passed
        )

        old_status = project.status
        advance_workflow(project, 'lod_loq', step.passed)
        
        # Log the validation action
        AuditLogger.log_validation_action(
            request.user,
            'submit',
            project,
            'lod_loq',
            {
                'result': result['status'],
                'lod': result['metrics'].get('lod'),
                'loq': result['metrics'].get('loq'),
                'slope': slope,
                'previous_project_status': old_status,
                'new_project_status': project.status
            }
        )

        response_data = {
            'status': result['status'],
            'metrics': result['metrics'],
            'justification': result['justification']
        }

        return Response(response_data)

    else:  # GET
        step = ValidationStep.objects.filter(project=project, step='lod_loq').first()
        if not step:
            return Response({'error': 'LOD/LOQ data not found'}, status=status.HTTP_404_NOT_FOUND)

        data = LODLOQData.objects.get(validation_step=step)
        serializer = LODLOQDataSerializer(data)
        return Response(serializer.data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsAnalystOrHigher])
def supporting_documents_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['file']
        file_type = request.data.get('file_type', 'other')
        description = request.data.get('description', '')
        validation_step_id = request.data.get('validation_step_id')
        
        # Validate file type
        allowed_extensions = ['.pdf', '.csv', '.jpg', '.jpeg', '.png', '.tiff', '.txt', '.xlsx', '.docx']
        file_ext = '.' + file.name.split('.')[-1].lower()
        if file_ext not in allowed_extensions:
            return Response({'error': f'File type not allowed. Allowed: {", ".join(allowed_extensions)}'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Validate file size (5MB max)
        if file.size > 5 * 1024 * 1024:
            return Response({'error': 'File size exceeds 5MB limit'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get validation step if provided
        validation_step = None
        if validation_step_id:
            validation_step = ValidationStep.objects.filter(id=validation_step_id, project=project).first()
        
        document = SupportingDocument.objects.create(
            project=project,
            validation_step=validation_step,
            file=file,
            file_type=file_type,
            file_name=file.name,
            file_size=file.size,
            description=description,
            uploaded_by=request.user
        )
        
        # Log the upload
        AuditLogger.log_project_action(
            request.user,
            'submit',
            project,
            {'action': 'uploaded_document', 'file_name': file.name, 'file_type': file_type}
        )
        
        return Response({
            'id': document.id,
            'file_name': document.file_name,
            'file_type': document.file_type,
            'file_size': document.file_size,
            'description': document.description,
            'uploaded_at': document.uploaded_at,
            'uploaded_by': document.uploaded_by.username,
            'file_url': f'/api/validation/projects/{project_id}/documents/{document.id}/download/'
        }, status=status.HTTP_201_CREATED)
    
    else:  # GET
        documents = SupportingDocument.objects.filter(project=project)
        
        # Filter by validation step if provided
        step_id = request.query_params.get('step_id')
        if step_id:
            documents = documents.filter(validation_step_id=step_id)
        
        data = []
        for doc in documents:
            data.append({
                'id': doc.id,
                'file_name': doc.file_name,
                'file_type': doc.file_type,
                'file_size': doc.file_size,
                'description': doc.description,
                'uploaded_at': doc.uploaded_at,
                'uploaded_by': doc.uploaded_by.username,
                'validation_step': doc.validation_step.step if doc.validation_step else None,
                'file_url': f'/api/validation/projects/{project_id}/documents/{doc.id}/download/'
            })
        
        return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAnalystOrHigher])
def download_document(request, project_id, document_id):
    project = get_object_or_404(Project, id=project_id)
    document = get_object_or_404(SupportingDocument, id=document_id, project=project)
    
    # Log the download
    AuditLogger.log_project_action(
        request.user,
        'submit',
        project,
        {'action': 'downloaded_document', 'file_name': document.file_name}
    )
    
    response = FileResponse(document.file.open(), as_attachment=True)
    response['Content-Disposition'] = f'attachment; filename="{document.file_name}"'
    return response


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAnalystOrHigher])
def delete_document(request, project_id, document_id):
    project = get_object_or_404(Project, id=project_id)
    document = get_object_or_404(SupportingDocument, id=document_id, project=project)
    
    # Only allow deletion by uploader or QA
    if request.user != document.uploaded_by and request.user.role != 'qa':
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    file_name = document.file_name
    document.file.delete()  # Delete the actual file
    document.delete()  # Delete the database record
    
    # Log the deletion
    AuditLogger.log_project_action(
        request.user,
        'delete',
        project,
        {'action': 'deleted_document', 'file_name': file_name}
    )
    
    return Response({'message': 'Document deleted successfully'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAnalystOrHigher])
def validation_summary_view(request, project_id):
    """Get comprehensive validation summary for a project including all validation steps."""
    project = get_object_or_404(Project, id=project_id)
    
    summary = {
        'project_id': project.id,
        'project_status': project.status,
        'validation_steps': {}
    }
    
    # Get linearity data
    linearity_step = ValidationStep.objects.filter(project=project, step='linearity').first()
    if linearity_step:
        try:
            data = LinearityData.objects.get(validation_step=linearity_step)
            summary['validation_steps']['linearity'] = {
                'completed': linearity_step.completed,
                'passed': linearity_step.passed,
                'data': {
                    'concentrations': data.concentrations,
                    'responses': data.responses,
                    'slope': data.slope,
                    'intercept': data.intercept,
                    'r_squared': data.r_squared
                }
            }
        except LinearityData.DoesNotExist:
            summary['validation_steps']['linearity'] = {
                'completed': linearity_step.completed,
                'passed': linearity_step.passed,
                'data': None
            }
    
    # Get accuracy data
    accuracy_step = ValidationStep.objects.filter(project=project, step='accuracy').first()
    if accuracy_step:
        try:
            data = AccuracyData.objects.get(validation_step=accuracy_step)
            summary['validation_steps']['accuracy'] = {
                'completed': accuracy_step.completed,
                'passed': accuracy_step.passed,
                'data': {
                    'level': data.level,
                    'measured_values': data.measured_values,
                    'mean_recovery': data.mean_recovery,
                    'rsd': data.rsd
                }
            }
        except AccuracyData.DoesNotExist:
            summary['validation_steps']['accuracy'] = {
                'completed': accuracy_step.completed,
                'passed': accuracy_step.passed,
                'data': None
            }
    
    # Get precision data
    precision_step = ValidationStep.objects.filter(project=project, step='precision').first()
    if precision_step:
        try:
            data = PrecisionData.objects.get(validation_step=precision_step)
            summary['validation_steps']['precision'] = {
                'completed': precision_step.completed,
                'passed': precision_step.passed,
                'data': {
                    'replicate_values': data.replicate_values,
                    'mean': data.mean,
                    'rsd': data.rsd
                }
            }
        except PrecisionData.DoesNotExist:
            summary['validation_steps']['precision'] = {
                'completed': precision_step.completed,
                'passed': precision_step.passed,
                'data': None
            }
    
    # Get LOD/LOQ data
    lodloq_step = ValidationStep.objects.filter(project=project, step='lod_loq').first()
    if lodloq_step:
        try:
            data = LODLOQData.objects.get(validation_step=lodloq_step)
            summary['validation_steps']['lod_loq'] = {
                'completed': lodloq_step.completed,
                'passed': lodloq_step.passed,
                'data': {
                    'blank_responses': data.blank_responses,
                    'slope': data.slope,
                    'lod': data.lod,
                    'loq': data.loq
                }
            }
        except LODLOQData.DoesNotExist:
            summary['validation_steps']['lod_loq'] = {
                'completed': lodloq_step.completed,
                'passed': lodloq_step.passed,
                'data': None
            }
    
    # Get parameter reviews if any exist
    parameter_reviews = ParameterReview.objects.filter(project=project)
    if parameter_reviews.exists():
        summary['parameter_reviews'] = []
        for review in parameter_reviews:
            summary['parameter_reviews'].append({
                'parameter_name': review.parameter_name,
                'decision': review.decision,
                'comments': review.comments,
                'reviewed_by': review.reviewed_by.username if review.reviewed_by else None,
                'reviewed_at': review.reviewed_at
            })
    
    return Response(summary)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsReviewerOrHigher])
def submit_review_view(request, project_id):
    """Submit detailed review with parameter reviews and final decision."""
    project = get_object_or_404(Project, id=project_id)
    
    if project.status != 'review':
        return Response(
            {'error': 'Project is not in review status'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    final_decision = request.data.get('final_decision')
    comments = request.data.get('comments')
    parameter_reviews_data = request.data.get('parameter_reviews', {})
    
    if not final_decision or not comments:
        return Response(
            {'error': 'Final decision and comments are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Save parameter reviews
    for param_name, review_data in parameter_reviews_data.items():
        ParameterReview.objects.create(
            project=project,
            parameter_name=param_name,
            decision=review_data.get('decision'),
            comments=review_data.get('comments'),
            reviewed_by=request.user
        )
    
    # Update project based on final decision
    if final_decision == 'approve':
        project.reviewer = request.user
        project.reviewer_comment = comments
        project.reviewed_at = timezone.now()
        project.save()
        
        AuditLogger.log_project_action(
            request.user,
            'review',
            project,
            {
                'final_decision': final_decision,
                'reviewer_comment': comments,
                'reviewed_at': str(timezone.now()),
                'parameter_reviews': list(parameter_reviews_data.keys())
            }
        )
        
        return Response({
            'message': 'Review submitted successfully. Project ready for QA approval.',
            'status': 'reviewed'
        })
    
    elif final_decision == 'reject':
        # Reset project to draft for re-validation
        old_status = project.status
        project.status = 'draft'
        project.reviewer = request.user
        project.reviewer_comment = comments
        project.reviewed_at = timezone.now()
        project.save()
        
        # Clear validation steps so they can be redone
        ValidationStep.objects.filter(project=project).delete()
        
        AuditLogger.log_project_action(
            request.user,
            'review',
            project,
            {
                'final_decision': final_decision,
                'reviewer_comment': comments,
                'reviewed_at': str(timezone.now()),
                'previous_status': old_status,
                'new_status': 'draft',
                'action': 'returned_for_revalidation'
            }
        )
        
        return Response({
            'message': 'Review submitted. Project returned to analyst for re-validation.',
            'status': 'draft'
        })
    
    elif final_decision == 'conditional':
        project.reviewer = request.user
        project.reviewer_comment = comments + ' [CONDITIONAL APPROVAL]'
        project.reviewed_at = timezone.now()
        project.save()
        
        AuditLogger.log_project_action(
            request.user,
            'review',
            project,
            {
                'final_decision': final_decision,
                'reviewer_comment': comments,
                'reviewed_at': str(timezone.now()),
                'parameter_reviews': list(parameter_reviews_data.keys())
            }
        )
        
        return Response({
            'message': 'Conditional review submitted. Project ready for QA approval with conditions.',
            'status': 'reviewed'
        })
    
    else:
        return Response(
            {'error': 'Invalid final decision'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
