from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.apps import apps

from assetflow.permissions import IsAssetManagerOrAdmin
from org.utils import log_activity
from .models import Asset
from .serializers import AssetSerializer

class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    filterset_fields = {
        'tag': ['exact', 'icontains'],
        'serial_number': ['exact', 'icontains'],
        'category': ['exact'],
        'status': ['exact'],
        'department': ['exact'],
        'location': ['exact', 'icontains'],
    }

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'history']:
            return [permissions.IsAuthenticated()]
        return [IsAssetManagerOrAdmin()]

    def perform_create(self, serializer):
        instance = serializer.save()
        log_activity(self.request.user, 'CREATE', instance, f"Registered asset {instance.name} ({instance.tag}).")

    def perform_update(self, serializer):
        instance = serializer.save()
        log_activity(self.request.user, 'UPDATE', instance, f"Updated asset {instance.name} ({instance.tag}).")

    def perform_destroy(self, instance):
        log_activity(self.request.user, 'DELETE', instance, f"Deleted asset {instance.name} ({instance.tag}).")
        instance.delete()

    @action(detail=True, methods=['get'], url_path='history')
    def history(self, request, pk=None):
        asset = self.get_object()

        allocation_history = []
        # Dynamically load Allocation model if it exists (Step 3)
        try:
            Allocation = apps.get_model('allocations', 'Allocation')
            allocations = Allocation.objects.filter(asset=asset).order_by('-id')
            for alloc in allocations:
                allocation_history.append({
                    "id": alloc.id,
                    "user": alloc.user.username if alloc.user else None,
                    "status": alloc.status,
                    "allocated_at": alloc.allocated_at.isoformat() if hasattr(alloc, 'allocated_at') and alloc.allocated_at else None,
                    "returned_at": alloc.returned_at.isoformat() if hasattr(alloc, 'returned_at') and alloc.returned_at else None,
                })
        except (LookupError, ValueError):
            pass

        # Stubbed maintenance history (Step 4)
        maintenance_history = []

        return Response({
            "allocations": allocation_history,
            "maintenance": maintenance_history
        }, status=status.HTTP_200_OK)
