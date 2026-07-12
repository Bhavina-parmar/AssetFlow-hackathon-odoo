from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuditCycleViewSet, AuditItemViewSet

router = DefaultRouter()
router.register(r'audit-cycles', AuditCycleViewSet, basename='auditcycle')
router.register(r'audit-items', AuditItemViewSet, basename='audititem')

urlpatterns = [
    path('', include(router.urls)),
]
