from rest_framework import serializers
from django.db.models import Q
from .models import Booking, BookingStatus

class BookingSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    booked_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'resource', 'start_time', 'end_time', 'booked_by', 'status']

    def validate_resource(self, value):
        if not value.is_bookable:
            raise serializers.ValidationError("This resource is not marked as bookable.")
        return value

    def validate(self, attrs):
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        resource = attrs.get('resource')

        # Fallbacks for partial updates
        if not resource and self.instance:
            resource = self.instance.resource
        if not start_time and self.instance:
            start_time = self.instance.start_time
        if not end_time and self.instance:
            end_time = self.instance.end_time

        if start_time >= end_time:
            raise serializers.ValidationError("End time must be strictly after start time.")

        # Single query with exclude to check for overlaps
        overlaps = Booking.objects.filter(
            resource=resource,
            status__in=[BookingStatus.UPCOMING, BookingStatus.ONGOING]
        ).exclude(
            Q(end_time__lte=start_time) |
            Q(start_time__gte=end_time)
        )

        # Exclude self when updating
        if self.instance:
            overlaps = overlaps.exclude(id=self.instance.id)

        if overlaps.exists():
            raise serializers.ValidationError("This resource is already booked during the requested time range.")

        return attrs
