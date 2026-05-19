from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils.timesince import timesince
from .models import AdminProfile, TenantProfile, Rule
from .services.notification_service import NotificationService
from .models import ActivityLog


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
    """Enhanced user profile context processor supporting both admin and tenant users with completion tracking"""
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
            completion_fields = {
                'full_name': bool(profile.full_name),
                'email': bool(profile.user.email),
                'phone': bool(profile.phone),
                'photo': bool(profile.photo),
            }
            completion_percentage = (sum(completion_fields.values()) / len(completion_fields)) * 100
            filled_fields_count = sum(completion_fields.values())
            
            return {
                'user_profile': profile,
                'is_admin': True,
                'is_tenant': False,
                'profile_completion': completion_percentage,
                'completion_fields': completion_fields,
                'filled_fields_count': filled_fields_count,
            }
        except AdminProfile.DoesNotExist:
            return {
                'user_profile': None,
                'is_admin': True,
                'is_tenant': False,
                'profile_completion': 0,
                'completion_fields': {},
            }
    
    # For tenant users
    else:
        try:
            profile = TenantProfile.objects.select_related('user', 'room').get(user=request.user)
            completion_fields = {
                'full_name': bool(profile.full_name),
                'email': bool(profile.user.email),
                'phone': bool(profile.phone),
                'photo': bool(profile.photo),
                'room': bool(profile.room)
            }
            completion_percentage = (sum(completion_fields.values()) / len(completion_fields)) * 100
            filled_fields_count = sum(completion_fields.values())
            
            return {
                'user_profile': profile,
                'is_admin': False,
                'is_tenant': True,
                'profile_completion': completion_percentage,
                'completion_fields': completion_fields,
                'filled_fields_count': filled_fields_count,
            }
        except TenantProfile.DoesNotExist:
            return {
                'user_profile': None,
                'is_admin': False,
                'is_tenant': True,
                'profile_completion': 0,
                'completion_fields': {},
            }


def system_stats(request):
    """Lightweight system statistics for authenticated users only"""
    if not request.user.is_authenticated:
        return {'system_stats': {}}
    
    cache_key = f'system_stats_{request.user.id}'
    stats = cache.get(cache_key)
    
    if stats is None:
        from .models import TenantProfile
        stats = {
            'total_tenants': TenantProfile.objects.count(),
        }
        cache.set(cache_key, stats, 60)
    
    return {'system_stats': stats}


def recent_activity(request):
    """Recent activity feed for authenticated users"""
    if not request.user.is_authenticated:
        return {'recent_activities': []}
    
    activities = ActivityLog.objects.select_related('user').order_by('-timestamp')[:3]
    
    return {'recent_activities': activities}


def recent_payments(request):
    """Recent payments context processor for dashboard."""
    if not request.user.is_authenticated:
        return {'recent_payments': []}
    
    try:
        from .models import Payment
        payments = Payment.objects.select_related('bill').order_by('-payment_date')[:5]
        return {'recent_payments': payments}
    except Exception:
        return {'recent_payments': []}


def notifications(request):
    """Notifications context processor for authenticated users."""
    if not request.user.is_authenticated:
        return {
            'notifications': [],
            'unread_count': 0,
        }

    try:
        from .models import Notification

        notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

        return {
            'notifications': notifications,
            'unread_count': unread_count,
        }
    except Exception:
        return {
            'notifications': [],
            'unread_count': 0,
        }


def app_settings(request):
    """Application settings context processor."""
    from django.conf import settings
    return {
        'app_name': getattr(settings, 'APP_NAME', 'RENTS'),
        'app_version': getattr(settings, 'VERSION', '3.0'),
        'debug_mode': settings.DEBUG,
    }


def active_rules(request):
    """Context processor for active rules in tenant templates."""
    if not request.user.is_authenticated or request.user.is_staff:
        return {'active_rules': []}
    rules = Rule.objects.filter(is_active=True)[:5]
    return {'active_rules': rules}
    

def rules_count(request):
    """Rules count for dashboards (active only) - available for all authenticated users."""
