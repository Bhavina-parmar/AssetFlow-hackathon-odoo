from rest_framework import serializers
from .models import Asset

class AssetSerializer(serializers.ModelSerializer):
    tag = serializers.CharField(read_only=True)

    class Meta:
        model = Asset
        fields = [
            'id', 'tag', 'name', 'category', 'department', 'serial_number',
            'acquisition_date', 'acquisition_cost', 'condition',
            'location', 'photo', 'is_bookable', 'status',
        ]
