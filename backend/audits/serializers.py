from rest_framework import serializers
from .models import AuditCycle, AuditItem

class AuditCycleSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)

    class Meta:
        model = AuditCycle
        fields = [
            'id', 'scope_department', 'scope_location', 
            'start_date', 'end_date', 'status', 'auditors'
        ]

class AuditItemSerializer(serializers.ModelSerializer):
    cycle = serializers.PrimaryKeyRelatedField(read_only=True)
    asset = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = AuditItem
        fields = ['id', 'cycle', 'asset', 'result']
