from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError

from assetflow.permissions import IsAdmin, IsDeptHeadOrAbove
from .models import Department, Category, DepartmentStatus
from .serializers import DepartmentSerializer, CategorySerializer
from .utils import log_activity

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    filterset_fields = ['name', 'parent', 'status', 'head']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsDeptHeadOrAbove()]

    def perform_create(self, serializer):
        instance = serializer.save()
        log_activity(self.request.user, 'CREATE', instance, f"Created department {instance.name}.")

    def perform_update(self, serializer):
        instance = serializer.save()
        log_activity(self.request.user, 'UPDATE', instance, f"Updated department {instance.name}.")

    def perform_destroy(self, instance):
        log_activity(self.request.user, 'DELETE', instance, f"Deleted department {instance.name}.")
        instance.delete()

    @action(detail=True, methods=['post'], url_path='activate')
    def activate(self, request, pk=None):
        department = self.get_object()
        old_status = department.status
        try:
            department.transition(DepartmentStatus.ACTIVE)
            log_activity(
                request.user, 
                'STATUS_CHANGE', 
                department, 
                f"Transitioned status of department '{department.name}' from {old_status} to {DepartmentStatus.ACTIVE}."
            )
            serializer = self.get_serializer(department)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='deactivate')
    def deactivate(self, request, pk=None):
        department = self.get_object()
        old_status = department.status
        try:
            department.transition(DepartmentStatus.INACTIVE)
            log_activity(
                request.user, 
                'STATUS_CHANGE', 
                department, 
                f"Transitioned status of department '{department.name}' from {old_status} to {DepartmentStatus.INACTIVE}."
            )
            serializer = self.get_serializer(department)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filterset_fields = ['name']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsAdmin()]

    def perform_create(self, serializer):
        instance = serializer.save()
        log_activity(self.request.user, 'CREATE', instance, f"Created category {instance.name}.")

    def perform_update(self, serializer):
        instance = serializer.save()
        log_activity(self.request.user, 'UPDATE', instance, f"Updated category {instance.name}.")

    def perform_destroy(self, instance):
        log_activity(self.request.user, 'DELETE', instance, f"Deleted category {instance.name}.")
        instance.delete()
