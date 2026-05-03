"""
Helper functions shared across views modules.
"""
import re
from django.db.models import Sum
from ..models import Room, TenantProfile, Bill, Payment, MaintenanceReport
from ..activity_utils import get_recent_activities


def parse_phone(raw):
    """Clean phone number to digits only."""
    if not raw:
        return None
    digits = re.sub(r"\D", "", str(raw))
    return int(digits) if digits else None


def get_available_rooms():
    """Get available rooms with dynamic inclusions."""
    rooms = [r for r in Room.objects.prefetch_related('dynamic_inclusions').order_by('floor', 'room_number') if not r.is_full()]
    # Add dynamic inclusions to each room
    for room in rooms:
        room.dynamic_inclusions_list = [{'id': inc.id, 'name': inc.name} for inc in room.dynamic_inclusions.all()]
    return rooms


def get_tenant_payment_status(tenant):
    """Get the latest bill status for a tenant."""
    latest_bill = Bill.objects.filter(tenant=tenant).order_by('-created_at').first()
    if latest_bill:
        return latest_bill.status
    return None


def get_dashboard_context():
    """Get context data for admin dashboard."""
    all_rooms     = Room.objects.all()
    total_tenants = TenantProfile.objects.count()
    total_beds    = sum(r.capacity for r in all_rooms)
    occupied_beds = sum(r.occupied_beds() for r in all_rooms)

    # Calculate total revenue from all payments
    total_revenue = Payment.objects.aggregate(
        total=Sum('amount')
    )['total'] or 0

    occupied_rooms = [r for r in all_rooms if r.occupied_beds() > 0]
    if len(occupied_rooms) < 3:
        vacant = [r for r in all_rooms if r.occupied_beds() == 0]
        occupied_rooms = occupied_rooms + vacant[:3 - len(occupied_rooms)]

    return {
        'total_tenants' : total_tenants,
        'vacant_rooms'  : sum(1 for r in all_rooms if not r.is_full()),
        'unpaid_bills'  : Bill.objects.exclude(status='paid').count(),
        'open_repairs'  : MaintenanceReport.objects.filter(status='open').count(),
        'recent_tenants': TenantProfile.objects.select_related('user', 'room').order_by('-created_at')[:7],
        'total_beds'    : total_beds,
        'occupied_beds' : occupied_beds,
        'vacant_beds'   : total_beds - occupied_beds,
        'occupancy_rate': (occupied_beds / total_beds * 100) if total_beds > 0 else 0,
        'recent_rooms'  : occupied_rooms[:3],
        'total_rooms': len(all_rooms),
        'total_revenue': total_revenue,
    }
