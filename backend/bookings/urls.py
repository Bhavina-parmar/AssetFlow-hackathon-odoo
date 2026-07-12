from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookingViewSet, ResourceBookingsView

router = DefaultRouter()
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('', include(router.urls)),
    path('resources/<int:id>/bookings/', ResourceBookingsView.as_view(), name='resource-bookings'),
]
