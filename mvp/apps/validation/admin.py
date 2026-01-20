from django.contrib import admin
from .models import ValidationStep, LinearityData, AccuracyData, PrecisionData, LODLOQData

class ValidationStepAdmin(admin.ModelAdmin):
    list_display = ('project', 'step', 'completed', 'passed', 'created_at')
    list_filter = ('step', 'completed', 'passed', 'created_at')
    search_fields = ('project__method_name',)
    readonly_fields = ('created_at',)

class LinearityDataAdmin(admin.ModelAdmin):
    list_display = ('validation_step', 'r_squared', 'passed', 'slope', 'intercept')
    list_filter = ('passed',)
    search_fields = ('validation_step__project__method_name',)
    readonly_fields = ('validation_step',)

class AccuracyDataAdmin(admin.ModelAdmin):
    list_display = ('validation_step', 'level', 'mean_recovery', 'rsd', 'passed')
    list_filter = ('level', 'passed')
    search_fields = ('validation_step__project__method_name',)
    readonly_fields = ('validation_step',)

class PrecisionDataAdmin(admin.ModelAdmin):
    list_display = ('validation_step', 'mean', 'rsd', 'passed')
    list_filter = ('passed',)
    search_fields = ('validation_step__project__method_name',)
    readonly_fields = ('validation_step',)

class LODLOQDataAdmin(admin.ModelAdmin):
    list_display = ('validation_step', 'lod', 'loq', 'passed')
    list_filter = ('passed',)
    search_fields = ('validation_step__project__method_name',)
    readonly_fields = ('validation_step',)

admin.site.register(ValidationStep, ValidationStepAdmin)
admin.site.register(LinearityData, LinearityDataAdmin)
admin.site.register(AccuracyData, AccuracyDataAdmin)
admin.site.register(PrecisionData, PrecisionDataAdmin)
admin.site.register(LODLOQData, LODLOQDataAdmin)
