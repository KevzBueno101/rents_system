"""
Centralized Notification Service for RENTS System

This service provides a unified interface for creating notifications
throughout the application, ensuring consistency and maintainability.

Usage:
    from accounts.services.notification_service import NotificationService
    
    # Create a notification
    NotificationService.create_notification(
        user=tenant.user,
        title="Payment Received",
        message="Your payment has been recorded successfully.",
        link="/tenant/billing/",
        notif_type="payment"
    )
"""

from django.contrib.auth.models import User
from django.urls import reverse
from typing import Optional, Union
from ..models import Notification


class NotificationService:
    """Centralized notification service for creating tenant-specific notifications"""
    
    @staticmethod
    def create_notification(
        user: User,
        title: str,
        message: str,
        link: Optional[str] = None,
        notif_type: Optional[str] = None,
        **kwargs
    ) -> Notification:
        """
        Create a notification for a specific user
        
        Args:
            user: The user who will receive the notification
            title: Notification title
            message: Notification message
            link: URL path for redirection (optional)
            notif_type: Type of notification (payment, billing, etc.)
            
        Returns:
            Notification object
            
        Raises:
            ValueError: If user is not provided
        """
        if not user:
            raise ValueError("User must be provided for notification creation")
            
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            link=link or NotificationService.get_default_link(notif_type),
            type=notif_type,
            **kwargs
        )
        
        return notification
    
    @staticmethod
    def get_default_link(notif_type: Optional[str]) -> str:
        """Get default link based on notification type"""
        default_links = {
            'payment': '/tenant/billing/',
            'billing': '/tenant/billing/',
            'maintenance': '/tenant/reports/',
            'announcement': '/tenant/dashboard/',
            'system': '/tenant/dashboard/',
            'reminder': '/tenant/dashboard/',
        }
        return default_links.get(notif_type, '/tenant/dashboard/')
    
    @staticmethod
    def create_payment_notification(tenant_user: User, amount: float = None) -> Notification:
        """Create payment-related notification"""
        title = "Payment Received"
        if amount:
            message = f"Your payment of ₱{amount:,.2f} has been recorded successfully."
        else:
            message = "Your payment has been recorded successfully."
        
        return NotificationService.create_notification(
            user=tenant_user,
            title=title,
            message=message,
            link="/tenant/billing/",
            notif_type="payment"
        )
    
    @staticmethod
    def create_billing_notification(tenant_user: User, bill_number: str = None) -> Notification:
        """Create billing-related notification"""
        title = "New Bill Generated"
        message = f"Bill {bill_number} has been generated for this month." if bill_number else "A new bill has been generated for this month."
        
        return NotificationService.create_notification(
            user=tenant_user,
            title=title,
            message=message,
            link="/tenant/billing/",
            notif_type="billing"
        )
    
    @staticmethod
    def create_maintenance_notification(tenant_user: User, status: str = None) -> Notification:
        """Create maintenance-related notification"""
        title = "Maintenance Update"
        message = f"Your maintenance request status has been updated to: {status}." if status else "Your maintenance request has been updated."
        
        return NotificationService.create_notification(
            user=tenant_user,
            title=title,
            message=message,
            link="/tenant/reports/",
            notif_type="maintenance"
        )
    
    @staticmethod
    def create_announcement_notification(tenant_user: User, announcement_title: str = None) -> Notification:
        """Create announcement notification"""
        title = "New Announcement"
        message = f"New announcement: {announcement_title}" if announcement_title else "You have a new announcement from the admin."
        
        return NotificationService.create_notification(
            user=tenant_user,
            title=title,
            message=message,
            link="/tenant/dashboard/",
            notif_type="announcement"
        )
    
    @staticmethod
    def get_user_notifications(user: User, limit: int = 10) -> tuple:
        """
        Get notifications for a specific user with unread count
        
        Args:
            user: User to get notifications for
            limit: Maximum number of notifications to return
            
        Returns:
            Tuple of (notifications, unread_count)
        """
        notifications = Notification.objects.filter(
            user=user
        ).select_related('user').order_by('-created_at')[:limit]
        
        unread_count = Notification.objects.filter(
            user=user,
            is_read=False
        ).count()
        
        return notifications, unread_count
    
    @staticmethod
    def mark_as_read(notification_id: int, user: User) -> bool:
        """
        Mark notification as read for security (user-specific)
        
        Args:
            notification_id: ID of notification to mark as read
            user: User attempting to mark notification as read
            
        Returns:
            True if successful, False otherwise
        """
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=user  # Security: ensures user can only mark their own notifications
            )
            notification.is_read = True
            notification.save(update_fields=['is_read'])
            return True
        except Notification.DoesNotExist:
            return False
    
    @staticmethod
    def mark_all_as_read(user: User) -> int:
        """
        Mark all notifications as read for a user
        
        Args:
            user: User to mark all notifications as read for
            
        Returns:
            Number of notifications marked as read
        """
        count = Notification.objects.filter(
            user=user,
            is_read=False
        ).update(is_read=True)
        
        return count
