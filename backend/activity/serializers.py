from rest_framework import serializers
from .models import ActivityLog

class ActivityLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.username', read_only=True)

    class Meta:
        model = ActivityLog
        fields = ['id', 'actor', 'actor_name', 'action', 'target_type', 'target_id', 'timestamp', 'meta']
