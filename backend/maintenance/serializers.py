from rest_framework import serializers
from .models import MaintenanceRequest

class MaintenanceRequestSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    technician = serializers.PrimaryKeyRelatedField(read_only=True)
    raised_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = MaintenanceRequest
        fields = [
            'id', 'asset', 'raised_by', 'issue_text', 
            'priority', 'photo', 'status', 'technician'
        ]
        read_only_fields = ['status', 'technician', 'raised_by']
