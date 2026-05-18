"""
WebSocket consumers for real-time notifications

Provides real-time notification delivery via WebSocket connections.
Only active if ENABLE_WEBSOCKET_NOTIFICATIONS is True.
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from django.db.models import Q

from .models import Notification


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications
    
    Handles:
    - Initial connection and authentication
    - Sending last 5 unread notifications on connect
    - Real-time notification delivery
    - Mark as read operations
    - Bulk operations
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        # Check if user is authenticated
        if self.scope["user"].is_anonymous:
            await self.close()
            return
        
        # Check if WebSocket notifications are enabled
        from django.conf import settings
        if not getattr(settings, 'ENABLE_WEBSOCKET_NOTIFICATIONS', False):
            await self.close()
            return
        
        self.user = self.scope["user"]
        self.group_name = f"notifications_{self.user.id}"
        
        # Join notification group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        # Accept connection
        await self.accept()
        
        # Send initial payload
        await self.send_initial_payload()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave notification group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'mark_read':
                await self.mark_read(data.get('id'))
            elif action == 'mark_all_read':
                await self.mark_all_read()
            elif action == 'delete':
                await self.delete_notification(data.get('id'))
            elif action == 'bulk_action':
                await self.bulk_action(data)
            else:
                await self.send_error("Unknown action")
                
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON")
        except Exception as e:
            await self.send_error(f"Error: {str(e)}")
    
    async def send_initial_payload(self):
        """Send initial data on connection"""
        # Get last 5 unread notifications
        notifications = await self.get_unread_notifications(limit=5)
        
        # Get unread count
        unread_count = await self.get_unread_count()
        
        await self.send(text_data=json.dumps({
            'type': 'initial_payload',
            'notifications': notifications,
            'unread_count': unread_count
        }))
    
    async def mark_read(self, notification_id):
        """Mark notification as read"""
        if not notification_id:
            await self.send_error("Notification ID required")
            return
        
        success = await self.mark_notification_read(notification_id)
        
        if success:
            await self.send(text_data=json.dumps({
                'type': 'read_update',
                'id': notification_id
            }))
            
            # Update unread count
            unread_count = await self.get_unread_count()
            await self.send(text_data=json.dumps({
                'type': 'unread_count',
                'count': unread_count
            }))
        else:
            await self.send_error("Failed to mark as read")
    
    async def mark_all_read(self):
        """Mark all notifications as read"""
        count = await self.mark_all_notifications_read()
        
        await self.send(text_data=json.dumps({
            'type': 'all_read_update',
            'count': count
        }))
        
        # Update unread count
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'count': 0
        }))
    
    async def delete_notification(self, notification_id):
        """Delete a notification"""
        if not notification_id:
            await self.send_error("Notification ID required")
            return
        
        success = await self.delete_notification_by_id(notification_id)
        
        if success:
            await self.send(text_data=json.dumps({
                'type': 'notification_deleted',
                'id': notification_id
            }))
            
            # Update unread count
            unread_count = await self.get_unread_count()
            await self.send(text_data=json.dumps({
                'type': 'unread_count',
                'count': unread_count
            }))
        else:
            await self.send_error("Failed to delete notification")
    
    async def bulk_action(self, data):
        """Handle bulk operations"""
        action = data.get('bulk_action')
        notification_ids = data.get('notification_ids', [])
        
        if action == 'mark_read':
            count = await self.mark_notifications_read(notification_ids)
            await self.send(text_data=json.dumps({
                'type': 'bulk_read_update',
                'count': count
            }))
        elif action == 'delete':
            count = await self.delete_notifications(notification_ids)
            await self.send(text_data=json.dumps({
                'type': 'bulk_delete_update',
                'count': count
            }))
        
        # Update unread count
        unread_count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'count': unread_count
        }))
    
    async def new_notification(self, event):
        """Handle new notification broadcast"""
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'notification': event['notification']
        }))
        
        # Update unread count
        unread_count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'count': unread_count
        }))
    
    async def read_update(self, event):
        """Handle read status update broadcast"""
        await self.send(text_data=json.dumps({
            'type': 'read_update',
            'id': event['id']
        }))
    
    async def unread_count_update(self, event):
        """Handle unread count update broadcast"""
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'count': event['count']
        }))
    
    async def send_error(self, message):
        """Send error message to client"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))
    
    @database_sync_to_async
    def get_unread_notifications(self, limit=5):
        """Get unread notifications for user"""
        notifications = Notification.objects.filter(
            user=self.user,
            is_read=False
        ).exclude(
            Q(expires_at__lt=timezone.now()) & Q(expires_at__isnull=False)
        ).select_related('dynamic_type').order_by('-created_at')[:limit]
        
        return [
            {
                'id': notif.id,
                'title': notif.title,
                'message': notif.message,
                'link': notif.link,
                'type': notif.type,
                'is_read': notif.is_read,
                'created_at': notif.created_at.isoformat(),
                'icon': notif.dynamic_type.icon if notif.dynamic_type else 'bi-info-circle',
                'color': notif.dynamic_type.color if notif.dynamic_type else 'primary',
            }
            for notif in notifications
        ]
    
    @database_sync_to_async
    def get_unread_count(self):
        """Get unread notification count"""
        return Notification.objects.filter(
            user=self.user,
            is_read=False
        ).exclude(
            Q(expires_at__lt=timezone.now()) & Q(expires_at__isnull=False)
        ).count()
    
    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark notification as read"""
        updated = Notification.objects.filter(
            id=notification_id,
            user=self.user,
            is_read=False
        ).update(is_read=True)
        return updated > 0
    
    @database_sync_to_async
    def mark_all_notifications_read(self):
        """Mark all notifications as read"""
        updated, _ = Notification.objects.filter(
            user=self.user,
            is_read=False
        ).update(is_read=True)
        return updated
    
    @database_sync_to_async
    def delete_notification_by_id(self, notification_id):
        """Delete notification by ID"""
        deleted, _ = Notification.objects.filter(
            id=notification_id,
            user=self.user
        ).delete()
        return deleted > 0
    
    @database_sync_to_async
    def mark_notifications_read(self, notification_ids):
        """Mark multiple notifications as read"""
        updated = Notification.objects.filter(
            id__in=notification_ids,
            user=self.user,
            is_read=False
        ).update(is_read=True)
        return updated
    
    @database_sync_to_async
    def delete_notifications(self, notification_ids):
        """Delete multiple notifications"""
        deleted, _ = Notification.objects.filter(
            id__in=notification_ids,
            user=self.user
        ).delete()
        return deleted
