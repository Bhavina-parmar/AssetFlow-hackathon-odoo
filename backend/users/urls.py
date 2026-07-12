from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoginView, SignupView, EmployeeViewSet

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employee')

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/signup/', SignupView.as_view(), name='auth-signup'),
    path('', include(router.urls)),
]
