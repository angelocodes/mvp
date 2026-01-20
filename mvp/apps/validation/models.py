from django.db import models
from django.conf import settings


class ValidationStep(models.Model):
    STEP_CHOICES = [
        ('linearity', 'Linearity'),
        ('accuracy', 'Accuracy'),
        ('precision', 'Precision'),
        ('lod_loq', 'LOD/LOQ'),
    ]
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)
    step = models.CharField(max_length=20, choices=STEP_CHOICES)
    completed = models.BooleanField(default=False)
    passed = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['project', 'step']


class LinearityData(models.Model):
    validation_step = models.OneToOneField(ValidationStep, on_delete=models.CASCADE)
    concentrations = models.JSONField()  # list of floats
    responses = models.JSONField()  # list of floats
    slope = models.FloatField(null=True)
    intercept = models.FloatField(null=True)
    r_squared = models.FloatField(null=True)
    passed = models.BooleanField(null=True)

    def __str__(self):
        return f"Linearity for {self.validation_step.project}"


class AccuracyData(models.Model):
    LEVEL_CHOICES = [
        ('80', '80%'),
        ('100', '100%'),
        ('120', '120%'),
    ]
    validation_step = models.OneToOneField(ValidationStep, on_delete=models.CASCADE)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    measured_values = models.JSONField()  # list of floats
    recovery = models.FloatField(null=True)
    mean_recovery = models.FloatField(null=True)
    rsd = models.FloatField(null=True)
    passed = models.BooleanField(null=True)


class PrecisionData(models.Model):
    validation_step = models.OneToOneField(ValidationStep, on_delete=models.CASCADE)
    replicate_values = models.JSONField()  # list of floats
    mean = models.FloatField(null=True)
    rsd = models.FloatField(null=True)
    passed = models.BooleanField(null=True)


class LODLOQData(models.Model):
    validation_step = models.OneToOneField(ValidationStep, on_delete=models.CASCADE)
    blank_responses = models.JSONField()  # list of floats
    slope = models.FloatField()  # from linearity
    lod = models.FloatField(null=True)
    loq = models.FloatField(null=True)
    passed = models.BooleanField(null=True)
