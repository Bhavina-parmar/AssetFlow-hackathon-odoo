from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AllocationViewSet, TransferRequestViewSet

router = DefaultRouter()
router.register(r'allocations', AllocationViewSet, basename='allocation')
router.register(r'transfers', TransferRequestViewSet, basename='transfer')

urlpatterns = [
    path('', include(router.urls)),
]
