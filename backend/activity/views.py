import datetime
from django.utils import timezone
from django.db.models import Count, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from assets.models import Asset, AssetStatus
from allocations.models import Allocation, AllocationStatus, TransferRequest, TransferStatus
from bookings.models import Booking, BookingStatus
from org.models import Category
from .models import ActivityLog
from .serializers import ActivityLogSerializer
from allocations.serializers import AllocationSerializer
from assets.serializers import AssetSerializer

class DashboardKPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = datetime.date.today()

        available_count = Asset.objects.filter(status=AssetStatus.AVAILABLE).count()
        allocated_count = Asset.objects.filter(status=AssetStatus.ALLOCATED).count()
        maintenance_count = Asset.objects.filter(status=AssetStatus.UNDER_MAINTENANCE).count()
        
        active_bookings_count = Booking.objects.filter(status=BookingStatus.ONGOING).count()
        pending_transfers_count = TransferRequest.objects.filter(status=TransferStatus.REQUESTED).count()
        
        upcoming_returns_count = Allocation.objects.filter(
            status=AllocationStatus.ACTIVE,
            expected_return_date__gte=today
        ).count()

        overdue_allocs = Allocation.objects.filter(
            status=AllocationStatus.ACTIVE,
            expected_return_date__lt=today
        )
        overdue_serializer = AllocationSerializer(overdue_allocs, many=True)

        return Response({
            "available_count": available_count,
            "allocated_count": allocated_count,
            "maintenance_count": maintenance_count,
            "active_bookings_count": active_bookings_count,
            "pending_transfers_count": pending_transfers_count,
            "upcoming_returns_count": upcoming_returns_count,
            "overdue_returns": overdue_serializer.data
        }, status=status.HTTP_200_OK)

class UtilizationReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # 1. Most used assets (sorted by allocation + booking count)
        assets_annotated = Asset.objects.annotate(
            bookings_count=Count('bookings', distinct=True),
            allocations_count=Count('allocations', distinct=True)
        )
        
        most_used_data = []
        for asset in assets_annotated:
            total_uses = asset.bookings_count + asset.allocations_count
            most_used_data.append({
                "id": asset.id,
                "tag": asset.tag,
                "name": asset.name,
                "bookings_count": asset.bookings_count,
                "allocations_count": asset.allocations_count,
                "total_uses": total_uses
            })
        # Sort descending by total uses
        most_used_data.sort(key=lambda x: x['total_uses'], reverse=True)

        # 2. Idle assets (unused in the last X days)
        idle_days = request.query_params.get('idle_days', 30)
        try:
            idle_days = int(idle_days)
        except ValueError:
            idle_days = 30

        cutoff_date = datetime.date.today() - datetime.timedelta(days=idle_days)
        cutoff_datetime = timezone.now() - datetime.timedelta(days=idle_days)

        # Find active / recently used assets
        used_asset_ids = set()
        
        # Recently allocated or currently allocated
        allocated_assets = Allocation.objects.filter(
            Q(status=AllocationStatus.ACTIVE) | Q(allocated_date__gte=cutoff_date)
        ).values_list('asset_id', flat=True)
        used_asset_ids.update(allocated_assets)

        # Recently booked
        booked_assets = Booking.objects.filter(
            end_time__gte=cutoff_datetime
        ).values_list('resource_id', flat=True)
        used_asset_ids.update(booked_assets)

        idle_assets = Asset.objects.exclude(id__in=used_asset_ids)
        idle_serializer = AssetSerializer(idle_assets, many=True)

        return Response({
            "most_used": most_used_data[:10],  # top 10
            "idle": idle_serializer.data
        }, status=status.HTTP_200_OK)

class MaintenanceFrequencyReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # 1. Grouped by asset
        assets_grouped = Asset.objects.annotate(
            maintenance_count=Count('maintenance_requests')
        ).order_by('-maintenance_count')
        
        by_asset_data = [{
            "id": asset.id,
            "tag": asset.tag,
            "name": asset.name,
            "maintenance_count": asset.maintenance_count
        } for asset in assets_grouped]

        # 2. Grouped by category
        categories_grouped = Category.objects.annotate(
            maintenance_count=Count('assets__maintenance_requests')
        ).order_by('-maintenance_count')
        
        by_category_data = [{
            "id": cat.id,
            "name": cat.name,
            "maintenance_count": cat.maintenance_count
        } for cat in categories_grouped]

        return Response({
            "by_asset": by_asset_data,
            "by_category": by_category_data
        }, status=status.HTTP_200_OK)

class NotificationsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # If ADMIN, show all logs
        from users.models import UserRole
        if user.role == UserRole.ADMIN:
            logs = ActivityLog.objects.all().order_by('-timestamp')[:50]
        else:
            # Show logs where actor is user, or linked to user's objects
            alloc_ids = list(Allocation.objects.filter(employee=user).values_list('id', flat=True))
            booking_ids = list(Booking.objects.filter(booked_by=user).values_list('id', flat=True))
            transfer_ids = list(TransferRequest.objects.filter(Q(from_employee=user) | Q(to_employee=user)).values_list('id', flat=True))
            
            q_filter = Q(actor=user)
            if alloc_ids:
                q_filter |= Q(target_type='Allocation', target_id__in=[str(x) for x in alloc_ids])
            if booking_ids:
                q_filter |= Q(target_type='Booking', target_id__in=[str(x) for x in booking_ids])
            if transfer_ids:
                q_filter |= Q(target_type='TransferRequest', target_id__in=[str(x) for x in transfer_ids])
                
            logs = ActivityLog.objects.filter(q_filter).order_by('-timestamp')[:50]

        serializer = ActivityLogSerializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# New report endpoints expected by the frontend
# ---------------------------------------------------------------------------

class AssetStatusBreakdownView(APIView):
    """GET /api/reports/asset-status-breakdown/ → [{name, value, color}]"""
    permission_classes = [permissions.IsAuthenticated]

    STATUS_COLORS = {
        'AVAILABLE':        '#22c55e',
        'ALLOCATED':        '#3b82f6',
        'RESERVED':         '#f59e0b',
        'UNDER_MAINTENANCE':'#f97316',
        'LOST':             '#ef4444',
        'RETIRED':          '#8b5cf6',
        'DISPOSED':         '#6b7280',
    }
    STATUS_LABELS = {
        'AVAILABLE': 'Available',
        'ALLOCATED': 'Allocated',
        'RESERVED': 'Reserved',
        'UNDER_MAINTENANCE': 'Maintenance',
        'LOST': 'Lost',
        'RETIRED': 'Retired',
        'DISPOSED': 'Disposed',
    }

    def get(self, request):
        from django.db.models import Count
        counts = Asset.objects.values('status').annotate(total=Count('id'))
        result = [
            {
                'name': self.STATUS_LABELS.get(row['status'], row['status']),
                'value': row['total'],
                'color': self.STATUS_COLORS.get(row['status'], '#6b7280'),
            }
            for row in counts if row['total'] > 0
        ]
        return Response(result, status=status.HTTP_200_OK)


class BookingTrendView(APIView):
    """GET /api/reports/booking-trend/ → [{day, bookings}] for current week"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = datetime.date.today()
        # Start from Monday of current week
        monday = today - datetime.timedelta(days=today.weekday())
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        result = []
        for i in range(7):
            day_date = monday + datetime.timedelta(days=i)
            count = Booking.objects.filter(
                start_time__date=day_date
            ).exclude(status=BookingStatus.CANCELLED).count()
            result.append({'day': days[i], 'bookings': count})
        return Response(result, status=status.HTTP_200_OK)


class BookingHeatmapView(APIView):
    """
    GET /api/reports/booking-heatmap/
    Returns booking counts grouped by hour slot × weekday.
    Format: [{slot: '09:00', Mon: 2, Tue: 0, ...}, ...]
    """
    permission_classes = [permissions.IsAuthenticated]

    SLOTS = [
        '08:00', '09:00', '10:00', '11:00',
        '12:00', '13:00', '14:00', '15:00',
        '16:00', '17:00', '18:00',
    ]
    DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    def get(self, request):
        bookings = Booking.objects.exclude(status=BookingStatus.CANCELLED)
        # Build a dict: {(weekday, hour): count}
        heat = {}
        for b in bookings:
            # Convert to local-aware date if tz-aware
            dt = b.start_time
            if hasattr(dt, 'astimezone'):
                import pytz
                try:
                    dt = dt.astimezone(pytz.utc)
                except Exception:
                    pass
            weekday = dt.weekday()   # 0=Mon
            hour = dt.hour
            slot = f'{hour:02d}:00'
            key = (weekday, slot)
            heat[key] = heat.get(key, 0) + 1

        result = []
        for slot in self.SLOTS:
            row = {'slot': slot}
            for i, day in enumerate(self.DAYS):
                row[day] = heat.get((i, slot), 0)
            result.append(row)
        return Response(result, status=status.HTTP_200_OK)


class LogsListView(APIView):
    """GET /api/logs/?module=&search= → paginated activity logs"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        logs = ActivityLog.objects.all().order_by('-timestamp')

        module = request.query_params.get('module', '')
        search = request.query_params.get('search', '')

        if module:
            logs = logs.filter(target_type__icontains=module)
        if search:
            logs = logs.filter(
                Q(action__icontains=search) |
                Q(target_type__icontains=search) |
                Q(actor__username__icontains=search)
            )

        logs = logs[:100]
        serializer = ActivityLogSerializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

