from .models import AdminProfile, TenantProfile


def admin_profile(request):
    """Legacy admin profile context processor - kept for backward compatibility"""
    if request.user.is_authenticated and request.user.is_staff:
        try:
            profile = request.user.adminprofile
        except AdminProfile.DoesNotExist:
            profile = None
    else:
        profile = None
    
    return {'admin_profile': profile}


def user_profile(request):
    """Enhanced user profile context processor supporting both admin and tenant users"""
    if not request.user.is_authenticated:
        return {
            'user_profile': None,
            'is_admin': False,
            'is_tenant': False,
        }
    
    # For admin users
    if request.user.is_staff:
        try:
            profile = AdminProfile.objects.select_related('user').get(user=request.user)
            return {
                'user_profile': profile,
                'is_admin': True,
                'is_tenant': False,
            }
        except AdminProfile.DoesNotExist:
            return {
                'user_profile': None,
                'is_admin': True,
                'is_tenant': False,
            }
    
    # For tenant users
    else:
        try:
            profile = TenantProfile.objects.select_related('user', 'room').get(user=request.user)
            return {
                'user_profile': profile,
                'is_admin': False,
                'is_tenant': True,
            }
        except TenantProfile.DoesNotExist:
            return {
                'user_profile': None,
                'is_admin': False,
                'is_tenant': True,
            }


def system_stats(request):
    """Lightweight system statistics for authenticated users only"""
    if not request.user.is_authenticated:
        return {'system_stats': {}}
    
    # Use count() queries only - no full object loading
    from django.core.cache import cache
    
    # Cache for 60 seconds to avoid repeated queries
    cache_key = f'system_stats_{request.user.id}'
    stats = cache.get(cache_key)
    
    if stats is None:
        stats = {
            'total_tenants': TenantProfile.objects.count(),
            'vacant_rooms': TenantProfile.objects.filter(room__isnull=False).count(),
            'unpaid_bills': 0,  # Will add after Bill model optimization
            'open_maintenance_reports': 0,  # Will add after Maintenance model optimization
        }
        cache.set(cache_key, stats, 60)
    
    return {'system_stats': stats}


def recent_activity(request):
    """Optimized recent activity feed for authenticated users"""
    if not request.user.is_authenticated:
        return {'recent_activities': []}
    
    from .activity_utils import get_recent_activities
    
    # Get only 3 most recent activities with user relation
    activities = get_recent_activities(limit=3).select_related('user')
    
    return {'recent_activities': activities}


def recent_payments(request):
    """Recent payment activities for billing section"""
    if not request.user.is_authenticated:
        return {'recent_payments': []}
    
    from .activity_utils import get_recent_payments
    
    # Get only 3 most recent payment activities with user relation
    payments = get_recent_payments(limit=3).select_related('user')
    
    return {'recent_payments': payments}


def app_settings(request):
    """Static application settings - no database queries"""
    from datetime import datetime
    
    return {
        'app_settings': {
            'name': 'RENTS System',
            'version': '2.6',
            'current_year': datetime.now().year,
        }
    }