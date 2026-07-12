from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
]
