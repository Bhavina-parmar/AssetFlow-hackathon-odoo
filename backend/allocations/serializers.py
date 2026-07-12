from rest_framework import serializers
from .models import Allocation, TransferRequest

class AllocationSerializer(serializers.ModelSerializer):
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Allocation
        fields = [
            'id', 'asset', 'employee', 'department', 
            'allocated_date', 'expected_return_date', 
            'returned_date', 'condition_note', 'status', 'is_overdue'
        ]

    def get_is_overdue(self, obj):
        return obj.is_overdue

class TransferRequestSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)

    class Meta:
        model = TransferRequest
        fields = [
            'id', 'asset', 'from_employee', 'to_employee', 
            'reason', 'status'
        ]
        read_only_fields = ['from_employee', 'status']
