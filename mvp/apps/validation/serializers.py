from rest_framework import serializers
from .models import ValidationStep, LinearityData, AccuracyData, PrecisionData, LODLOQData


class ValidationStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidationStep
        fields = ['id', 'step', 'completed', 'passed', 'created_at']


class LinearityDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinearityData
        fields = ['id', 'concentrations', 'responses', 'slope', 'intercept', 'r_squared', 'passed']


class LinearitySubmitSerializer(serializers.Serializer):
    concentrations = serializers.ListField(child=serializers.FloatField())
    responses = serializers.ListField(child=serializers.FloatField())


class AccuracyDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccuracyData
        fields = ['id', 'level', 'measured_values', 'recovery', 'mean_recovery', 'rsd', 'passed']


class AccuracySubmitSerializer(serializers.Serializer):
    level = serializers.ChoiceField(choices=['80', '100', '120'])
    measured_values = serializers.ListField(child=serializers.FloatField())


class PrecisionDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrecisionData
        fields = ['id', 'replicate_values', 'mean', 'rsd', 'passed']


class PrecisionSubmitSerializer(serializers.Serializer):
    replicate_values = serializers.ListField(child=serializers.FloatField())


class LODLOQDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = LODLOQData
        fields = ['id', 'blank_responses', 'slope', 'lod', 'loq', 'passed']


class LODLOQSubmitSerializer(serializers.Serializer):
    blank_responses = serializers.ListField(child=serializers.FloatField())
    slope = serializers.FloatField()
