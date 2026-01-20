from rest_framework import serializers
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'created_by', 'method_name', 'method_type', 'technique',
            'guideline', 'product_name', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['method_name', 'method_type', 'technique', 'guideline', 'product_name']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
