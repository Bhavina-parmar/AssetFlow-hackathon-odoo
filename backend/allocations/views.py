import datetime
from django.db import transaction
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from assetflow.permissions import IsDeptHeadOrAbove
from assets.models import Asset, AssetStatus
from org.utils import log_activity
from .models import Allocation, AllocationStatus, TransferRequest, TransferStatus
from .serializers import AllocationSerializer, TransferRequestSerializer

class AllocationViewSet(viewsets.ModelViewSet):
    queryset = Allocation.objects.all()
    serializer_class = AllocationSerializer
    filterset_fields = ['asset', 'employee', 'department', 'status']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsDeptHeadOrAbove()]

    def create(self, request, *args, **kwargs):
        # We override create to handle the AVAILABLE status check and return 409
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        asset = serializer.validated_data['asset']
        
        # Check asset's current status is AVAILABLE
        if asset.status != AssetStatus.AVAILABLE:
            # Find the active allocation holder details
            active_alloc = Allocation.objects.filter(asset=asset, status=AllocationStatus.ACTIVE).first()
            
            holder_data = None
            if active_alloc:
                holder_data = {
                    "name": active_alloc.employee.username if active_alloc.employee else None,
                    "department": active_alloc.department.name if active_alloc.department else None
                }
            
            return Response({
                "detail": f"Asset is currently held by {holder_data['name'] if holder_data else 'another process'}.",
                "holder": holder_data
            }, status=status.HTTP_409_CONFLICT)
            
        with transaction.atomic():
            # Save the allocation
            allocation = serializer.save()
            
            # Transition asset status to ALLOCATED
            try:
                asset.transition(AssetStatus.ALLOCATED)
            except DjangoValidationError as e:
                raise ValidationError({"detail": str(e)})
                
            # Log activity
            log_activity(
                request.user, 
                'ALLOCATE', 
                allocation, 
                f"Allocated asset {asset.tag} to {allocation.employee}."
            )
            
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'], url_path='return')
    def return_asset(self, request, pk=None):
        allocation = self.get_object()
        
        if allocation.status == AllocationStatus.RETURNED:
            return Response({"detail": "Asset has already been returned."}, status=status.HTTP_400_BAD_REQUEST)
            
        asset = allocation.asset
        condition_note = request.data.get('condition_note', '')
        
        with transaction.atomic():
            # Update allocation status
            allocation.status = AllocationStatus.RETURNED
            allocation.returned_date = datetime.date.today()
            if condition_note:
                allocation.condition_note = condition_note
            allocation.save()
            
            # Revert asset status to AVAILABLE
            try:
                asset.transition(AssetStatus.AVAILABLE)
            except DjangoValidationError as e:
                raise ValidationError({"detail": str(e)})
                
            # Log activity
            log_activity(
                request.user, 
                'RETURN', 
                allocation, 
                f"Asset {asset.tag} returned by {allocation.employee}."
            )
            
        serializer = self.get_serializer(allocation)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TransferRequestViewSet(viewsets.ModelViewSet):
    queryset = TransferRequest.objects.all()
    serializer_class = TransferRequestSerializer
    filterset_fields = ['asset', 'from_employee', 'to_employee', 'status']

    def get_permissions(self):
        if self.action in ['approve', 'reject']:
            return [IsDeptHeadOrAbove()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        instance = serializer.save(from_employee=self.request.user)
        log_activity(
            self.request.user, 
            'TRANSFER_REQUEST', 
            instance, 
            f"Requested transfer of asset {instance.asset.tag} to {instance.to_employee}."
        )

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        transfer = self.get_object()
        
        if transfer.status != TransferStatus.REQUESTED:
            return Response({"detail": "Transfer request is not in REQUESTED status."}, status=status.HTTP_400_BAD_REQUEST)
            
        asset = transfer.asset
        
        with transaction.atomic():
            # 1. Close the old active allocation
            active_alloc = Allocation.objects.filter(asset=asset, status=AllocationStatus.ACTIVE).first()
            if active_alloc:
                active_alloc.status = AllocationStatus.RETURNED
                active_alloc.returned_date = datetime.date.today()
                active_alloc.condition_note = f"Transferred to {transfer.to_employee.username}. Reason: {transfer.reason}"
                active_alloc.save()
                log_activity(
                    request.user, 
                    'RETURN', 
                    active_alloc, 
                    f"Closed allocation of {asset.tag} to {active_alloc.employee} due to transfer."
                )
                
            # 2. Create the new allocation for the new holder
            new_alloc = Allocation.objects.create(
                asset=asset,
                employee=transfer.to_employee,
                department=transfer.to_employee.headed_departments.first() if hasattr(transfer.to_employee, 'headed_departments') else None,
                expected_return_date=active_alloc.expected_return_date if active_alloc else datetime.date.today() + datetime.timedelta(days=30),
                status=AllocationStatus.ACTIVE
            )
            log_activity(
                request.user, 
                'ALLOCATE', 
                new_alloc, 
                f"Created new allocation for {asset.tag} to {transfer.to_employee} via transfer."
            )
            
            # Ensure asset status is set to ALLOCATED (which it already should be)
            if asset.status != AssetStatus.ALLOCATED:
                asset.status = AssetStatus.ALLOCATED
                asset.save()
                
            # 3. Mark transfer request as APPROVED
            transfer.status = TransferStatus.APPROVED
            transfer.save()
            
            log_activity(
                request.user, 
                'TRANSFER_APPROVE', 
                transfer, 
                f"Approved transfer of asset {asset.tag} from {transfer.from_employee} to {transfer.to_employee}."
            )
            
        serializer = self.get_serializer(transfer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        transfer = self.get_object()
        
        if transfer.status != TransferStatus.REQUESTED:
            return Response({"detail": "Transfer request is not in REQUESTED status."}, status=status.HTTP_400_BAD_REQUEST)
            
        transfer.status = TransferStatus.REJECTED
        transfer.save()
        
        log_activity(
            request.user, 
            'TRANSFER_REJECT', 
            transfer, 
            f"Rejected transfer of asset {transfer.asset.tag} to {transfer.to_employee}."
        )
        
        serializer = self.get_serializer(transfer)
        return Response(serializer.data, status=status.HTTP_200_OK)
