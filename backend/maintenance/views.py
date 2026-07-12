from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import get_user_model
from django.db import transaction

from assetflow.permissions import IsAssetManagerOrAdmin
from assets.models import AssetStatus
from org.utils import log_activity
from .models import MaintenanceRequest, MaintenanceStatus
from .serializers import MaintenanceRequestSerializer

User = get_user_model()

class MaintenanceRequestViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceRequest.objects.all()
    serializer_class = MaintenanceRequestSerializer
    filterset_fields = ['asset', 'raised_by', 'priority', 'status', 'technician']
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save(raised_by=self.request.user)
        log_activity(
            self.request.user, 
            'MAINTENANCE_RAISE', 
            instance, 
            f"Raised maintenance request for asset {instance.asset.tag}."
        )

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        self.permission_classes = [IsAssetManagerOrAdmin]
        self.check_permissions(request)
        
        request_obj = self.get_object()
        asset = request_obj.asset

        with transaction.atomic():
            try:
                request_obj.transition(MaintenanceStatus.APPROVED)
                asset.transition(AssetStatus.UNDER_MAINTENANCE)
            except DjangoValidationError as e:
                raise ValidationError({"detail": str(e)})

            log_activity(
                request.user, 
                'MAINTENANCE_APPROVE', 
                request_obj, 
                f"Approved maintenance request for asset {asset.tag}."
            )

        serializer = self.get_serializer(request_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        self.permission_classes = [IsAssetManagerOrAdmin]
        self.check_permissions(request)
        
        request_obj = self.get_object()

        with transaction.atomic():
            try:
                request_obj.transition(MaintenanceStatus.REJECTED)
            except DjangoValidationError as e:
                raise ValidationError({"detail": str(e)})

            log_activity(
                request.user, 
                'MAINTENANCE_REJECT', 
                request_obj, 
                f"Rejected maintenance request for asset {request_obj.asset.tag}."
            )

        serializer = self.get_serializer(request_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='assign-technician')
    def assign_technician(self, request, pk=None):
        self.permission_classes = [IsAssetManagerOrAdmin]
        self.check_permissions(request)
        
        request_obj = self.get_object()
        tech_id = request.data.get('technician')
        if not tech_id:
            return Response({"detail": "Technician ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        technician = get_object_or_404 = User.objects.filter(id=tech_id).first()
        if not technician:
            return Response({"detail": "Technician not found."}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            request_obj.technician = technician
            try:
                request_obj.transition(MaintenanceStatus.TECHNICIAN_ASSIGNED)
            except DjangoValidationError as e:
                raise ValidationError({"detail": str(e)})

            log_activity(
                request.user, 
                'MAINTENANCE_ASSIGN', 
                request_obj, 
                f"Assigned technician {technician.username} to maintenance request {request_obj.id}."
            )

        serializer = self.get_serializer(request_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='start')
    def start_work(self, request, pk=None):
        request_obj = self.get_object()

        with transaction.atomic():
            try:
                request_obj.transition(MaintenanceStatus.IN_PROGRESS)
            except DjangoValidationError as e:
                raise ValidationError({"detail": str(e)})

            log_activity(
                request.user, 
                'MAINTENANCE_START', 
                request_obj, 
                f"Started work on maintenance request {request_obj.id}."
            )

        serializer = self.get_serializer(request_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='resolve')
    def resolve(self, request, pk=None):
        request_obj = self.get_object()
        asset = request_obj.asset

        with transaction.atomic():
            try:
                request_obj.transition(MaintenanceStatus.RESOLVED)
                asset.transition(AssetStatus.AVAILABLE)
            except DjangoValidationError as e:
                raise ValidationError({"detail": str(e)})

            log_activity(
                request.user, 
                'MAINTENANCE_RESOLVE', 
                request_obj, 
                f"Resolved maintenance request for asset {asset.tag}."
            )

        serializer = self.get_serializer(request_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)
