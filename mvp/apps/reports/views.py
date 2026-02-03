from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from io import BytesIO
from apps.projects.models import Project
from apps.validation.models import ValidationStep, LinearityData, AccuracyData, PrecisionData, LODLOQData
from apps.users.permissions import IsAnalystOrHigher
from apps.audit.utils import AuditLogger


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsAnalystOrHigher])
def report_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        if project.status != 'approved':
            return Response({'error': 'Project must be approved to generate report'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate comprehensive PDF
        pdf_content = generate_comprehensive_pdf(project)
        
        project.report_generated = True
        project.save()
        
        # Log report generation
        AuditLogger.log_project_action(
            request.user,
            'submit',
            project,
            {'action': 'generated_report', 'generated_by': request.user.username}
        )

        return Response({'message': 'Report generated successfully'})

    else:  # GET
        if not project.report_generated:
            return Response({'error': 'Report not generated yet'}, status=status.HTTP_404_NOT_FOUND)

        # Generate comprehensive PDF on the fly
        pdf_content = generate_comprehensive_pdf(project)
        
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="validation_report_{project.id}.pdf"'
        return response


def generate_comprehensive_pdf(project):
    """Generate a comprehensive validation report PDF with all metrics"""
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Header
    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, height - 50, "Analytical Method Validation Report")
    
    # Subtitle
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 70, f"Method: {project.method_name}")
    p.drawString(50, height - 85, f"Product: {project.product_name}")
    
    # Horizontal line
    p.setStrokeColor(colors.black)
    p.setLineWidth(1)
    p.line(50, height - 95, width - 50, height - 95)
    
    y = height - 120
    
    # Project Information Section
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "1. Project Information")
    y -= 20
    
    p.setFont("Helvetica", 10)
    info_lines = [
        f"Method Name: {project.method_name}",
        f"Method Type: {project.method_type}",
        f"Technique: {project.get_technique_display()}",
        f"Guideline: {project.get_guideline_display()}",
        f"Product: {project.product_name}",
        f"Status: {project.get_status_display()}",
        f"Created By: {project.created_by.username}",
        f"Created At: {project.created_at.strftime('%Y-%m-%d %H:%M')}",
    ]
    
    if project.reviewer:
        info_lines.append(f"Reviewer: {project.reviewer.username}")
        info_lines.append(f"Reviewed At: {project.reviewed_at.strftime('%Y-%m-%d %H:%M') if project.reviewed_at else 'N/A'}")
    
    if project.qa_approver:
        info_lines.append(f"QA Approver: {project.qa_approver.username}")
        info_lines.append(f"Approved At: {project.approved_at.strftime('%Y-%m-%d %H:%M') if project.approved_at else 'N/A'}")
    
    for line in info_lines:
        p.drawString(70, y, line)
        y -= 15
    
    y -= 20
    
    # Validation Results Summary
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "2. Validation Results Summary")
    y -= 20
    
    steps = ValidationStep.objects.filter(project=project).order_by('created_at')
    
    if steps.exists():
        p.setFont("Helvetica-Bold", 11)
        p.drawString(70, y, "Validation Step")
        p.drawString(250, y, "Status")
        p.drawString(350, y, "Result")
        y -= 15
        
        p.setFont("Helvetica", 10)
        for step in steps:
            status_text = "COMPLETED" if step.completed else "PENDING"
            result_text = "PASS" if step.passed else "FAIL"
            result_color = colors.green if step.passed else colors.red
            
            p.drawString(70, y, step.get_step_display())
            p.drawString(250, y, status_text)
            p.setFillColor(result_color)
            p.drawString(350, y, result_text)
            p.setFillColor(colors.black)
            y -= 15
    else:
        p.setFont("Helvetica", 10)
        p.drawString(70, y, "No validation data available")
        y -= 15
    
    y -= 20
    
    # Check if we need a new page
    if y < 150:
        p.showPage()
        y = height - 50
    
    # Detailed Validation Metrics
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "3. Detailed Validation Metrics")
    y -= 25
    
    # Linearity Details
    linearity_step = steps.filter(step='linearity').first()
    if linearity_step and linearity_step.passed:
        linearity_data = LinearityData.objects.filter(validation_step=linearity_step).first()
        if linearity_data:
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, y, "3.1 Linearity")
            y -= 18
            
            p.setFont("Helvetica", 10)
            metrics = [
                f"R² (Correlation Coefficient): {linearity_data.r_squared:.4f} (Required: ≥ 0.99)",
                f"Slope: {linearity_data.slope:.4f}",
                f"Intercept: {linearity_data.intercept:.4f}",
                f"Status: {'PASS' if linearity_data.passed else 'FAIL'}",
                "",
                "Concentrations: " + ", ".join([str(c) for c in linearity_data.concentrations]),
                "Responses: " + ", ".join([str(r) for r in linearity_data.responses]),
            ]
            
            for line in metrics:
                p.drawString(70, y, line)
                y -= 14
            
            y -= 10
    
    # Check page break
    if y < 200:
        p.showPage()
        y = height - 50
    
    # Accuracy Details
    accuracy_step = steps.filter(step='accuracy').first()
    if accuracy_step and accuracy_step.passed:
        accuracy_data = AccuracyData.objects.filter(validation_step=accuracy_step).first()
        if accuracy_data:
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, y, "3.2 Accuracy (Recovery)")
            y -= 18
            
            p.setFont("Helvetica", 10)
            metrics = [
                f"Level: {accuracy_data.level}%",
                f"Mean Recovery: {accuracy_data.mean_recovery:.2f}% (Required: 80-120%)",
                f"RSD: {accuracy_data.rsd:.2f}%",
                f"Status: {'PASS' if accuracy_data.passed else 'FAIL'}",
                "",
                "Measured Values: " + ", ".join([str(v) for v in accuracy_data.measured_values]),
            ]
            
            for line in metrics:
                p.drawString(70, y, line)
                y -= 14
            
            y -= 10
    
    # Check page break
    if y < 200:
        p.showPage()
        y = height - 50
    
    # Precision Details
    precision_step = steps.filter(step='precision').first()
    if precision_step and precision_step.passed:
        precision_data = PrecisionData.objects.filter(validation_step=precision_step).first()
        if precision_data:
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, y, "3.3 Precision (Repeatability)")
            y -= 18
            
            p.setFont("Helvetica", 10)
            metrics = [
                f"Mean: {precision_data.mean:.4f}",
                f"RSD: {precision_data.rsd:.2f}% (Required: ≤ 2.0% for n≥6, ≤ 5.0% for n=3-5)",
                f"Status: {'PASS' if precision_data.passed else 'FAIL'}",
                "",
                "Replicate Values: " + ", ".join([str(v) for v in precision_data.replicate_values]),
            ]
            
            for line in metrics:
                p.drawString(70, y, line)
                y -= 14
            
            y -= 10
    
    # Check page break
    if y < 200:
        p.showPage()
        y = height - 50
    
    # LOD/LOQ Details
    lod_loq_step = steps.filter(step='lod_loq').first()
    if lod_loq_step and lod_loq_step.passed:
        lod_loq_data = LODLOQData.objects.filter(validation_step=lod_loq_step).first()
        if lod_loq_data:
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, y, "3.4 LOD/LOQ")
            y -= 18
            
            p.setFont("Helvetica", 10)
            metrics = [
                f"LOD (Limit of Detection): {lod_loq_data.lod:.4f}",
                f"LOQ (Limit of Quantification): {lod_loq_data.loq:.4f}",
                f"Slope: {lod_loq_data.slope:.4f}",
                f"Status: {'PASS' if lod_loq_data.passed else 'FAIL'}",
                "",
                "Blank Responses: " + ", ".join([str(v) for v in lod_loq_data.blank_responses]),
            ]
            
            for line in metrics:
                p.drawString(70, y, line)
                y -= 14
            
            y -= 10
    
    y -= 20
    
    # Check page break
    if y < 150:
        p.showPage()
        y = height - 50
    
    # Conclusion
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "4. Conclusion")
    y -= 20
    
    p.setFont("Helvetica", 10)
    all_passed = all(step.passed for step in steps) if steps.exists() else False
    
    if all_passed and project.status == 'approved':
        conclusion = (
            "The analytical method validation has been completed successfully. All validation parameters "
            f"(Linearity, Accuracy, Precision, and LOD/LOQ) meet the acceptance criteria specified in "
            f"{project.get_guideline_display()}. The method is approved for routine use."
        )
    else:
        conclusion = (
            "The analytical method validation has been completed. However, some validation parameters "
            "did not meet the acceptance criteria. Please review the detailed results above."
        )
    
    # Wrap text
    words = conclusion.split()
    line = ""
    for word in words:
        if len(line + " " + word) < 80:
            line += " " + word if line else word
        else:
            p.drawString(70, y, line)
            y -= 14
            line = word
    
    if line:
        p.drawString(70, y, line)
    
    y -= 30
    
    # Footer with signatures
    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, y, "Signatures:")
    y -= 25
    
    p.setFont("Helvetica", 10)
    if project.reviewer:
        p.drawString(70, y, f"Reviewed By: _________________    {project.reviewer.username}")
        y -= 20
    
    if project.qa_approver:
        p.drawString(70, y, f"Approved By (QA): _________________    {project.qa_approver.username}")
        y -= 20
    
    # Footer line
    p.setFont("Helvetica", 8)
    p.drawString(50, 30, f"Report Generated: {project.approved_at.strftime('%Y-%m-%d %H:%M') if project.approved_at else 'N/A'}")
    p.drawString(width - 150, 30, "Page 1 of 1")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer.getvalue()
