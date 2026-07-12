from django.urls import path
from .views import DashboardKPIView, UtilizationReportView, MaintenanceFrequencyReportView, NotificationsView

urlpatterns = [
    path('dashboard/kpis/', DashboardKPIView.as_view(), name='dashboard-kpis'),
    path('reports/utilization/', UtilizationReportView.as_view(), name='report-utilization'),
    path('reports/maintenance-frequency/', MaintenanceFrequencyReportView.as_view(), name='report-maintenance'),
    path('notifications/', NotificationsView.as_view(), name='notifications'),
]
