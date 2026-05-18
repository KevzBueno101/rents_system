"""
Dynamic Notification Service

Enhanced notification service with template rendering, user preferences,
and real-time delivery capabilities.
"""

import json
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.template import Template, Context
from django.utils import timezone
from typing import Optional, Dict, Any

from .models import (
    NotificationType, 
    NotificationTemplate, 
    UserNotificationPreference,
)
from accounts.models import Notification


class DynamicNotificationService:
    """Enhanced notification service with dynamic types and templates"""
    
    @classmethod
    def create(
        cls,
        user: User,
        type_code: str,
        context: Dict[str, Any] = None,
        channel: str = None,
        link: str = None,
        expires_at=None,
    ) -> Notification:
        """
        Create a dynamic notification with template rendering
        
        Args:
            user: The user who will receive the notification
            type_code: Maps to NotificationType.code
            context: Template variable data for rendering
            channel: Override user preference if provided
            link: URL path for redirection
            expires_at: When notification should expire
            
        Returns:
            Notification instance
        """
        context = context or {}
        
        # Get or create notification type
        notification_type = cls._get_or_create_type(type_code)
        
        # Get user preference
        user_pref = cls._get_user_preference(user)
        
        # Determine delivery channel
        delivery_channel = channel or cls._resolve_channel(user_pref, type_code)
        
        # Get and render template
        template = NotificationTemplateRenderer.get_template(type_code)
        rendered = NotificationTemplateRenderer.render(template, context) if template else {
            'title': context.get('title', 'Notification'),
            'message': context.get('message', str(context))
        }
        
        # Create notification
        notification = Notification.objects.create(
            user=user,
            title=rendered['title'],
            message=rendered['message'],
            link=link or cls._get_default_link(type_code),
            type=type_code,  # Legacy field
            dynamic_type=notification_type,
            context_data=context,
            delivery_channel=delivery_channel,
            expires_at=expires_at,
        )
        
        # Trigger async delivery if needed
        if delivery_channel != 'in_app':
            cls._trigger_async_delivery(notification, delivery_channel)
        
        # Real-time broadcast if enabled
        if getattr(settings, 'ENABLE_WEBSOCKET_NOTIFICATIONS', False):
            cls._broadcast_notification(user.id, notification)
        
        return notification
    
    @classmethod
    def bulk_mark_read(cls, user: User, notification_ids: list[int]) -> int:
        """Mark multiple notifications as read. Returns count updated."""
        updated = Notification.objects.filter(
            user=user,
            id__in=notification_ids,
            is_read=False
        ).update(is_read=True)
        
        # Broadcast updates if WebSocket enabled
        if updated and getattr(settings, 'ENABLE_WEBSOCKET_NOTIFICATIONS', False):
            cls._broadcast_read_update(user.id, notification_ids)
        
        return updated
    
    @classmethod
    def mark_all_read(cls, user: User) -> int:
        """Mark all unread notifications for user. Returns count."""
        updated = Notification.objects.filter(
            user=user,
            is_read=False
        ).update(is_read=True)
        
        # Broadcast update if WebSocket enabled
        if updated and getattr(settings, 'ENABLE_WEBSOCKET_NOTIFICATIONS', False):
            cls._broadcast_unread_count(user.id, 0)
        
        return updated
    
    @classmethod
    def delete_by_type(cls, user: User, type_code: str) -> int:
        """Delete all of user's notifications for a type. Returns count."""
        notification_type = cls._get_or_create_type(type_code)
        deleted, _ = Notification.objects.filter(
            user=user,
            dynamic_type=notification_type
        ).delete()
        
        return deleted
    
    @classmethod
    def get_filtered(cls, user: User, filters: Dict[str, Any]) -> models.QuerySet:
        """
        Get filtered notifications with optimized queries
        
        Args:
            user: The user to get notifications for
            filters: Dict with keys: type_code, is_read, date_from, date_to
            
        Returns:
            QuerySet with select_related('dynamic_type')
        """
        queryset = Notification.objects.filter(
            user=user
        ).select_related('dynamic_type')
        
        # Apply filters
        if 'type_code' in filters:
            notification_type = cls._get_or_create_type(filters['type_code'])
            queryset = queryset.filter(dynamic_type=notification_type)
        
        if 'is_read' in filters:
            queryset = queryset.filter(is_read=filters['is_read'])
        
        if 'date_from' in filters:
            queryset = queryset.filter(created_at__gte=filters['date_from'])
        
        if 'date_to' in filters:
            queryset = queryset.filter(created_at__lte=filters['date_to'])
        
        # Exclude expired notifications
        queryset = queryset.exclude(
            models.Q(expires_at__lt=timezone.now()) & models.Q(expires_at__isnull=False)
        )
        
        return queryset.order_by('-created_at')
    
    @classmethod
    def _get_or_create_type(cls, type_code: str) -> NotificationType:
        """Get existing notification type or create if auto-create is enabled"""
        try:
            return NotificationType.objects.get(code=type_code)
        except NotificationType.DoesNotExist:
            if getattr(settings, 'DYNAMIC_NOTIFICATION_AUTO_CREATE', True):
                return NotificationType.objects.create(
                    code=type_code,
                    label=type_code.replace('_', ' ').title(),
                    icon='bi-info-circle',
                    color='primary',
                    is_active=True
                )
            else:
                raise ValueError(f"Notification type '{type_code}' not found and auto-create is disabled")
    
    @classmethod
    def _get_user_preference(cls, user: User) -> UserNotificationPreference:
        """Get or create user notification preferences"""
        pref, created = UserNotificationPreference.objects.get_or_create(
            user=user,
            defaults={
                'default_channel': 'in_app',
                'type_overrides': {},
            }
        )
        return pref
    
    @classmethod
    def _resolve_channel(cls, pref: UserNotificationPreference, type_code: str) -> str:
        """Resolve delivery channel based on user preferences"""
        # Check type-specific override
        if type_code in pref.type_overrides:
            return pref.type_overrides[type_code]
        
        # Use default channel
        return pref.default_channel
    
    @classmethod
    def _get_default_link(cls, type_code: str) -> str:
        """Get default link for notification type"""
        link_mapping = {
            'payment': '/tenant/billing/',
            'billing': '/tenant/billing/',
            'maintenance': '/tenant/maintenance/',
            'announcement': '/tenant/dashboard/',
            'system': '/tenant/dashboard/',
            'reminder': '/tenant/dashboard/',
            'payment_proof': '/tenant/billing/',
        }
        return link_mapping.get(type_code, '/tenant/dashboard/')
    
    @classmethod
    def _trigger_async_delivery(cls, notification: Notification, channel: str):
        """Trigger async delivery tasks"""
        if channel == 'email':
            from .tasks import send_email_notification
            send_email_notification.delay(notification.id)
        elif channel == 'sms':
            from .tasks import send_sms_notification
            send_sms_notification.delay(notification.id)
        elif channel == 'all':
            from .tasks import send_email_notification, send_sms_notification
            send_email_notification.delay(notification.id)
            send_sms_notification.delay(notification.id)
    
    @classmethod
    def _broadcast_notification(cls, user_id: int, notification: Notification):
        """Broadcast new notification via WebSocket"""
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"notifications_{user_id}",
                {
                    'type': 'new_notification',
                    'notification': cls._serialize_notification(notification)
                }
            )
        except ImportError:
            # Channels not installed or not configured
            pass
    
    @classmethod
    def _broadcast_read_update(cls, user_id: int, notification_ids: list[int]):
        """Broadcast read status update via WebSocket"""
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"notifications_{user_id}",
                {
                    'type': 'read_update',
                    'ids': notification_ids
                }
            )
        except ImportError:
            pass
    
    @classmethod
    def _broadcast_unread_count(cls, user_id: int, count: int):
        """Broadcast unread count update via WebSocket"""
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"notifications_{user_id}",
                {
                    'type': 'unread_count',
                    'count': count
                }
            )
        except ImportError:
            pass
    
    @classmethod
    def _serialize_notification(cls, notification: Notification) -> Dict[str, Any]:
        """Serialize notification for WebSocket transmission"""
        return {
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'link': notification.link,
            'type': notification.type,
            'is_read': notification.is_read,
            'created_at': notification.created_at.isoformat(),
            'icon': notification.dynamic_type.icon if notification.dynamic_type else 'bi-info-circle',
            'color': notification.dynamic_type.color if notification.dynamic_type else 'primary',
        }


class NotificationTemplateRenderer:
    """Template rendering service for notifications"""
    
    @staticmethod
    def render(template: NotificationTemplate, context: Dict[str, Any]) -> Dict[str, str]:
        """
        Render notification template with context data
        
        Args:
            template: NotificationTemplate instance
            context: Template variable data
            
        Returns:
            Dict with 'title' and 'message' keys
        """
        # Create Django template context
        django_context = Context(context)
        
        # Render title
        title_template = Template(template.title_template)
        title = title_template.render(django_context)
        
        # Render body
        body_template = Template(template.body_template)
        message = body_template.render(django_context)
        
        return {
            'title': title,
            'message': message
        }
    
    @staticmethod
    def get_template(type_code: str, language: str = 'en') -> Optional[NotificationTemplate]:
        """
        Get notification template for type and language
        
        Args:
            type_code: Notification type code
            language: Language code (defaults to 'en')
            
        Returns:
            NotificationTemplate or None
        """
        try:
            # Try to get template for specific language
            return NotificationTemplate.objects.get(
                notification_type__code=type_code,
                language=language
            )
        except NotificationTemplate.DoesNotExist:
            try:
                # Fall back to English
                return NotificationTemplate.objects.get(
                    notification_type__code=type_code,
                    language='en'
                )
            except NotificationTemplate.DoesNotExist:
                # No template found
                return None


# Backward compatibility wrapper
def create_notification(user, notification_type: str, message: str, link=''):
    """
    Legacy interface - still works. Internally delegates to
    DynamicNotificationService.create() using type_code=notification_type
    and context={'message': message}.
    """
    return DynamicNotificationService.create(
        user=user,
        type_code=notification_type,
        context={'message': message},
        link=link,
    )
