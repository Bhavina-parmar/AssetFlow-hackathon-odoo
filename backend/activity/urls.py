from django.urls import path
from .views import (
    DashboardKPIView,
    UtilizationReportView,
    MaintenanceFrequencyReportView,
    NotificationsView,
    AssetStatusBreakdownView,
    BookingTrendView,
    BookingHeatmapView,
    LogsListView,
)

urlpatterns = [
    path('dashboard/kpis/', DashboardKPIView.as_view(), name='dashboard-kpis'),
    path('reports/utilization/', UtilizationReportView.as_view(), name='report-utilization'),
    path('reports/maintenance-frequency/', MaintenanceFrequencyReportView.as_view(), name='report-maintenance'),
    path('reports/asset-status-breakdown/', AssetStatusBreakdownView.as_view(), name='report-asset-status'),
    path('reports/booking-trend/', BookingTrendView.as_view(), name='report-booking-trend'),
    path('reports/booking-heatmap/', BookingHeatmapView.as_view(), name='report-booking-heatmap'),
    path('notifications/', NotificationsView.as_view(), name='notifications'),
    path('logs/', LogsListView.as_view(), name='logs-list'),
]
