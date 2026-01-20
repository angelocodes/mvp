from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from apps.projects.models import Project
from apps.validation.models import ValidationStep
from apps.users.permissions import IsAnalystOrHigher


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsAnalystOrHigher])
def report_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        if project.status != 'approved':
            return Response({'error': 'Project must be approved to generate report'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate PDF
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Title
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, height - 50, f"Validation Report for {project.method_name}")

        # Project details
        p.setFont("Helvetica", 12)
        y = height - 80
        p.drawString(100, y, f"Product: {project.product_name}")
        y -= 20
        p.drawString(100, y, f"Technique: {project.get_technique_display()}")
        y -= 20
        p.drawString(100, y, f"Guideline: {project.get_guideline_display()}")

        # Validation results
        y -= 40
        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, y, "Validation Results")
        y -= 20
        p.setFont("Helvetica", 12)

        steps = ValidationStep.objects.filter(project=project)
        for step in steps:
            p.drawString(100, y, f"{step.get_step_display()}: {'PASS' if step.passed else 'FAIL'}")
            y -= 20

        p.showPage()
        p.save()

        buffer.seek(0)
        project.report_generated = True
        project.save()

        return Response({'message': 'Report generated'})

    else:  # GET
        if not project.report_generated:
            return Response({'error': 'Report not generated yet'}, status=status.HTTP_404_NOT_FOUND)

        # Generate PDF on the fly
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, height - 50, f"Validation Report for {project.method_name}")

        p.setFont("Helvetica", 12)
        y = height - 80
        p.drawString(100, y, f"Product: {project.product_name}")

        p.showPage()
        p.save()

        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="report_{project.id}.pdf"'
        return response
