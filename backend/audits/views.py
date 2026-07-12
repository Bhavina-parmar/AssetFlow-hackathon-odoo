from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction

from assets.models import Asset, AssetStatus
from org.utils import log_activity
from .models import AuditCycle, AuditItem, AuditCycleStatus, AuditResult
from .serializers import AuditCycleSerializer, AuditItemSerializer

class AuditCycleViewSet(viewsets.ModelViewSet):
    queryset = AuditCycle.objects.all()
    serializer_class = AuditCycleSerializer
    filterset_fields = ['scope_department', 'status']
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            cycle = serializer.save()

            # Query assets in scope
            assets = Asset.objects.all()
            if cycle.scope_department:
                assets = assets.filter(department=cycle.scope_department)
            if cycle.scope_location:
                assets = assets.filter(location__icontains=cycle.scope_location)

            # Auto-populate AuditItems
            audit_items = []
            for asset in assets:
                audit_items.append(AuditItem(cycle=cycle, asset=asset))
            AuditItem.objects.bulk_create(audit_items)

            log_activity(
                request.user, 
                'AUDIT_CYCLE_CREATE', 
                cycle, 
                f"Created audit cycle {cycle.id} covering {len(audit_items)} assets in scope."
            )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['get'], url_path='discrepancies')
    def discrepancies(self, request, pk=None):
        cycle = self.get_object()
        # Discrepancy means result is not VERIFIED (so it includes MISSING, DAMAGED, or still null)
        discrepancies = AuditItem.objects.filter(cycle=cycle).exclude(result=AuditResult.VERIFIED)
        serializer = AuditItemSerializer(discrepancies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='close')
    def close_cycle(self, request, pk=None):
        cycle = self.get_object()

        if cycle.status == AuditCycleStatus.CLOSED:
            return Response({"detail": "Audit cycle is already closed."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # 1. Update status to CLOSED
            cycle.status = AuditCycleStatus.CLOSED
            cycle.save()

            log_activity(
                request.user, 
                'AUDIT_CYCLE_CLOSE', 
                cycle, 
                f"Closed audit cycle {cycle.id}."
            )

            # 2. Bulk update assets marked as MISSING to status LOST
            missing_items = AuditItem.objects.filter(cycle=cycle, result=AuditResult.MISSING)
            lost_count = 0
            for item in missing_items:
                asset = item.asset
                try:
                    asset.transition(AssetStatus.LOST)
                    log_activity(
                        request.user, 
                        'STATUS_CHANGE', 
                        asset, 
                        f"Asset status transitioned to LOST because it was marked MISSING in audit cycle {cycle.id}."
                    )
                    lost_count += 1
                except DjangoValidationError as e:
                    # Log error or continue to avoid blocking the bulk operations
                    pass

        serializer = self.get_serializer(cycle)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AuditItemViewSet(viewsets.ModelViewSet):
    queryset = AuditItem.objects.all()
    serializer_class = AuditItemSerializer
    filterset_fields = ['cycle', 'asset', 'result']
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='mark')
    def mark(self, request, pk=None):
        item = self.get_object()
        cycle = item.cycle

        # 1. Check if cycle is OPEN
        if cycle.status != AuditCycleStatus.OPEN:
            return Response(
                {"detail": "Cannot mark item in a closed audit cycle."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Check if user is an assigned auditor
        if not cycle.auditors.filter(id=request.user.id).exists():
            raise PermissionDenied("You are not an assigned auditor for this cycle.")

        result_val = request.data.get('result')
        if result_val not in AuditResult.values:
            return Response({"detail": "Invalid audit result value."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            item.result = result_val
            item.save()

            log_activity(
                request.user, 
                'AUDIT_ITEM_MARK', 
                item, 
                f"Marked asset {item.asset.tag} as {result_val} in audit cycle {cycle.id}."
            )

        serializer = self.get_serializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)
