from django.db import models
from django.conf import settings


class Project(models.Model):
    METHOD_TYPE_CHOICES = [
        ('assay', 'Assay'),
    ]
    TECHNIQUE_CHOICES = [
        ('hplc', 'HPLC'),
        ('uv', 'UV'),
    ]
    GUIDELINE_CHOICES = [
        ('ich_q2', 'ICH Q2'),
    ]
    STATUS_CHOICES = [
        ('draft', 'DRAFT'),
        ('linearity', 'LINEARITY'),
        ('accuracy', 'ACCURACY'),
        ('precision', 'PRECISION'),
        ('lod_loq', 'LOD/LOQ'),
        ('review', 'REVIEW'),
        ('approved', 'APPROVED'),
    ]

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    method_name = models.CharField(max_length=255)
    method_type = models.CharField(max_length=20, choices=METHOD_TYPE_CHOICES, default='assay')
    technique = models.CharField(max_length=20, choices=TECHNIQUE_CHOICES)
    guideline = models.CharField(max_length=20, choices=GUIDELINE_CHOICES, default='ich_q2')
    product_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_projects')
    reviewer_comment = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    qa_approver = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_projects')
    approved_at = models.DateTimeField(null=True, blank=True)
    report_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.method_name} - {self.product_name}"

    class Meta:
        ordering = ['-created_at']
