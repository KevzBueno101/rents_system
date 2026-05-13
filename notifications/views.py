"""
Views for dynamic notification system

Provides user-facing views for notification center, preferences,
and bulk operations.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, UpdateView
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.utils.dateparse import parse_date
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse
import json

from accounts.models import Notification
from .models import NotificationType, UserNotificationPreference
from .services import DynamicNotificationService


class NotificationCenterView(LoginRequiredMixin, ListView):
    """
    Enhanced notification center with filtering and pagination
    """
    model = Notification
    template_name = 'notifications/center.html'
    context_object_name = 'notifications'
    paginate_by = 20
    
    def get_queryset(self):
        """Get filtered notifications"""
        queryset = DynamicNotificationService.get_filtered(
            self.request.user,
            self.get_filters()
        )
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add additional context data"""
        context = super().get_context_data(**kwargs)
        
        # Add filter context
        context.update({
            'available_types': NotificationType.objects.filter(is_active=True),
            'active_filters': self.get_filters(),
            'unread_count': self.get_unread_count(),
        })
        
        return context
    
    def get_filters(self):
        """Parse filters from GET parameters"""
        filters = {}
        
        # Type filter
        type_code = self.request.GET.get('type')
        if type_code:
            filters['type_code'] = type_code
        
        # Status filter
        status = self.request.GET.get('status')
        if status in ['read', 'unread']:
            filters['is_read'] = (status == 'read')
        
        # Date range filters
        date_from = self.request.GET.get('from')
        if date_from:
            try:
                filters['date_from'] = parse_date(date_from)
            except ValueError:
                pass
        
        date_to = self.request.GET.get('to')
        if date_to:
            try:
                filters['date_to'] = parse_date(date_to)
            except ValueError:
                pass
        
        return filters
    
    def get_unread_count(self):
        """Get unread notification count"""
        return Notification.objects.filter(
            user=self.request.user,
            is_read=False
        ).exclude(
            expires_at__lt=timezone.now()
        ).count()


class NotificationPreferencesView(LoginRequiredMixin, UpdateView):
    """
    User notification preferences management
    """
    model = UserNotificationPreference
    template_name = 'notifications/preferences.html'
    success_url = reverse_lazy('notification_preferences')
    
    def get_object(self):
        """Get or create user preferences"""
        obj, created = UserNotificationPreference.objects.get_or_create(
            user=self.request.user,
            defaults={
                'default_channel': 'in_app',
                'type_overrides': {},
            }
        )
        return obj
    
    def get_context_data(self, **kwargs):
        """Add notification types to context"""
        context = super().get_context_data(**kwargs)
        context['notification_types'] = NotificationType.objects.filter(is_active=True)
        return context
    
    def form_valid(self, form):
        """Handle form submission"""
        response = super().form_valid(form)
        messages.success(self.request, 'Notification preferences updated successfully!')
        return response


@login_required
@csrf_protect
@require_http_methods(["POST"])
def bulk_action(request):
    """
    Handle bulk notification operations
    """
    try:
        data = json.loads(request.body)
        action = data.get('action')
        
        if action == 'mark_read':
            notification_ids = data.get('ids', [])
            if notification_ids:
                affected = DynamicNotificationService.bulk_mark_read(request.user, notification_ids)
            else:
                affected = DynamicNotificationService.mark_all_read(request.user)
        
        elif action == 'delete':
            notification_ids = data.get('ids', [])
            if notification_ids:
                with transaction.atomic():
                    affected, _ = Notification.objects.filter(
                        id__in=notification_ids,
                        user=request.user
                    ).delete()
            else:
                affected = 0
        
        elif action == 'delete_by_type':
            type_code = data.get('type_code')
            if type_code:
                affected = DynamicNotificationService.delete_by_type(request.user, type_code)
            else:
                affected = 0
        
        elif action == 'mark_all_read':
            affected = DynamicNotificationService.mark_all_read(request.user)
        
        else:
            return JsonResponse({'success': False, 'error': 'Unknown action'})
        
        return JsonResponse({
            'success': True,
            'affected': affected
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def notification_stream(request):
    """
    Server-Sent Events endpoint for real-time notifications
    Fallback when WebSocket is not available
    """
    def event_stream():
        """Stream notification updates"""
        last_id = 0
        
        while True:
            # Get new notifications
            notifications = Notification.objects.filter(
                user=request.user,
                id__gt=last_id
            ).order_by('id')
            
            for notif in notifications:
                yield f"event: notification\ndata: {json.dumps({
                    'id': notif.id,
                    'title': notif.title,
                    'message': notif.message,
                    'link': notif.link,
                    'type': notif.type,
                    'is_read': notif.is_read,
                    'created_at': notif.created_at.isoformat(),
                })}\n\n"
                last_id = notif.id
            
            # Check for read updates
            # This is a simplified version - in production, you'd want
            # a more sophisticated way to track changes
            yield f"event: heartbeat\ndata: {json.dumps({'timestamp': timezone.now().isoformat()})}\n\n"
            
            # Wait before next check
            import time
            time.sleep(2)
    
    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


@login_required
@csrf_protect
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """
    Mark single notification as read (AJAX endpoint)
    """
    try:
        affected = DynamicNotificationService.bulk_mark_read(request.user, [notification_id])
        
        if affected > 0:
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Notification not found'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@csrf_protect
@require_http_methods(["POST"])
def mark_all_notifications_read(request):
    """
    Mark all notifications as read (AJAX endpoint)
    """
    try:
        affected = DynamicNotificationService.mark_all_read(request.user)
        return JsonResponse({'success': True, 'affected': affected})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@csrf_protect
@require_http_methods(["POST"])
def delete_notification(request, notification_id):
    """
    Delete single notification (AJAX endpoint)
    """
    try:
        with transaction.atomic():
            deleted, _ = Notification.objects.filter(
                id=notification_id,
                user=request.user
            ).delete()
        
        if deleted > 0:
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Notification not found'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def notification_badge(request):
    """
    Template tag endpoint for notification badge count
    """
    count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).exclude(
        expires_at__lt=timezone.now()
    ).count()
    
    return JsonResponse({'count': count})


@login_required
def notification_stats(request):
    """
    Get notification statistics for dashboard
    """
    stats = {
        'unread_count': Notification.objects.filter(
            user=request.user,
            is_read=False
        ).exclude(
            expires_at__lt=timezone.now()
        ).count(),
        'total_count': Notification.objects.filter(
            user=request.user
        ).count(),
        'type_counts': {}
    }
    
    # Count by type
    for notif_type in NotificationType.objects.filter(is_active=True):
        count = Notification.objects.filter(
            user=request.user,
            dynamic_type=notif_type,
            is_read=False
        ).exclude(
            expires_at__lt=timezone.now()
        ).count()
        
        if count > 0:
            stats['type_counts'][notif_type.code] = {
                'label': notif_type.label,
                'count': count,
                'icon': notif_type.icon,
                'color': notif_type.color
            }
    
    return JsonResponse(stats)
