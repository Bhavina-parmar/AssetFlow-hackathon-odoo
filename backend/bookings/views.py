from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction

from assets.models import Asset, AssetStatus
from org.utils import log_activity
from .models import Booking, BookingStatus
from .serializers import BookingSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    filterset_fields = ['resource', 'booked_by', 'status']
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save(booked_by=self.request.user)
        log_activity(
            self.request.user, 
            'BOOK', 
            instance, 
            f"Created upcoming booking for resource {instance.resource.tag}."
        )

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        booking = self.get_object()
        
        if booking.status in [BookingStatus.COMPLETED, BookingStatus.CANCELLED]:
            return Response(
                {"detail": f"Booking has already been {booking.status.lower()}."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        asset = booking.resource
        
        with transaction.atomic():
            # If the booking is currently ONGOING and the asset status is RESERVED, 
            # transition the asset status back to AVAILABLE
            if booking.status == BookingStatus.ONGOING and asset.status == AssetStatus.RESERVED:
                try:
                    asset.transition(AssetStatus.AVAILABLE)
                    log_activity(
                        request.user, 
                        'STATUS_CHANGE', 
                        asset, 
                        f"Reverted status of asset {asset.tag} to AVAILABLE due to cancelled booking."
                    )
                except Exception:
                    pass
            
            booking.status = BookingStatus.CANCELLED
            booking.save()
            
            log_activity(
                request.user, 
                'BOOKING_CANCEL', 
                booking, 
                f"Cancelled booking {booking.id} for resource {asset.tag}."
            )
            
        serializer = self.get_serializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ResourceBookingsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id=None):
        asset = get_object_or_404(Asset, id=id)
        # Fetch all bookings for this resource
        bookings = Booking.objects.filter(resource=asset).order_by('start_time')
        
        # Calendar friendly structure
        data = []
        for b in bookings:
            data.append({
                "id": b.id,
                "start_time": b.start_time.isoformat(),
                "end_time": b.end_time.isoformat(),
                "booked_by": b.booked_by.username,
                "status": b.status
            })
            
        return Response(data, status=status.HTTP_200_OK)
