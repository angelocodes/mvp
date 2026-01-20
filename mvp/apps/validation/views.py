from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from apps.projects.models import Project
from apps.users.permissions import IsAnalystOrHigher
from .models import ValidationStep, LinearityData, AccuracyData, PrecisionData, LODLOQData
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
        advance_workflow(project, 'linearity', step.passed)

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

        advance_workflow(project, 'accuracy', step.passed)

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


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAnalystOrHigher])
def submit_precision(request, project_id):
    project = get_object_or_404(Project, id=project_id)

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

    advance_workflow(project, 'precision', step.passed)

    response_data = {
        'status': result['status'],
        'metrics': result['metrics'],
        'justification': result['justification']
    }

    return Response(response_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAnalystOrHigher])
def get_precision(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    step = ValidationStep.objects.filter(project=project, step='precision').first()
    if not step:
        return Response({'error': 'Precision data not found'}, status=status.HTTP_404_NOT_FOUND)

    data = PrecisionData.objects.get(validation_step=step)
    serializer = PrecisionDataSerializer(data)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAnalystOrHigher])
def submit_lod_loq(request, project_id):
    project = get_object_or_404(Project, id=project_id)

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

    advance_workflow(project, 'lod_loq', step.passed)

    response_data = {
        'status': result['status'],
        'metrics': result['metrics'],
        'justification': result['justification']
    }

    return Response(response_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAnalystOrHigher])
def get_lod_loq(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    step = ValidationStep.objects.filter(project=project, step='lod_loq').first()
    if not step:
        return Response({'error': 'LOD/LOQ data not found'}, status=status.HTTP_404_NOT_FOUND)

    data = LODLOQData.objects.get(validation_step=step)
    serializer = LODLOQDataSerializer(data)
    return Response(serializer.data)
