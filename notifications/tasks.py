"""
Celery tasks for async notification delivery

Handles email, SMS, and cleanup tasks for the dynamic notification system.
"""

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.db import transaction
from typing import Optional

from accounts.models import Notification


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_notification(self, notification_id: int):
    """
    Send notification via email
    
    Args:
        notification_id: ID of the notification to send
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with transaction.atomic():
            notification = Notification.objects.select_for_update().get(id=notification_id)
            
            # Check if already sent
            if notification.is_emailed:
                return True
            
            # Check if notification is expired
            if notification.expires_at and notification.expires_at < timezone.now():
                return False
            
            # Prepare email content
            subject = notification.title
            message = notification.message
            from_email = getattr(settings, 'NOTIFICATION_EMAIL_FROM', settings.DEFAULT_FROM_EMAIL)
            
            # Send email
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=[notification.user.email],
                fail_silently=False,
            )
            
            # Mark as emailed
            notification.is_emailed = True
            notification.save(update_fields=['is_emailed'])
            
            return True
            
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_sms_notification(self, notification_id: int):
    """
    Send notification via SMS
    
    Args:
        notification_id: ID of the notification to send
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with transaction.atomic():
            notification = Notification.objects.select_for_update().get(id=notification_id)
            
            # Check if already sent
            if notification.is_sms_sent:
                return True
            
            # Check if notification is expired
            if notification.expires_at and notification.expires_at < timezone.now():
                return False
            
            # Get user phone number
            phone_number = getattr(notification.user, 'phone', None)
            if not phone_number:
                return False
            
            # TODO: Integrate with SMS service (Twilio, etc.)
            # For now, just mark as sent
            # sms_service.send_sms(phone_number, notification.message)
            
            # Mark as SMS sent
            notification.is_sms_sent = True
            notification.save(update_fields=['is_sms_sent'])
            
            return True
            
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc)


@shared_task
def expire_old_notifications():
    """
    Clean up expired notifications
    
    This task should be run periodically (e.g., daily) via Celery Beat
    """
    expiry_days = getattr(settings, 'NOTIFICATION_EXPIRY_DAYS', 90)
    cutoff_date = timezone.now() - timezone.timedelta(days=expiry_days)
    
    # Delete expired notifications
    deleted_count, _ = Notification.objects.filter(
        created_at__lt=cutoff_date
    ).delete()
    
    return deleted_count


@shared_task
def cleanup_test_notifications():
    """
    Clean up test notifications (notifications with 'test' in title or message)
    
    This task can be run to clean up development/test notifications
    """
    deleted_count, _ = Notification.objects.filter(
        models.Q(title__icontains='test') | 
        models.Q(message__icontains='test')
    ).delete()
    
    return deleted_count


@shared_task
def send_bulk_notification(
    user_ids: list[int],
    type_code: str,
    context: dict = None,
    channel: str = 'in_app',
    link: str = None
):
    """
    Send notification to multiple users
    
    Args:
        user_ids: List of user IDs to send notification to
        type_code: Notification type code
        context: Template context data
        channel: Delivery channel
        link: Notification link
        
    Returns:
        dict: Results with success count and failed user IDs
    """
    from django.contrib.auth.models import User
    from .services import DynamicNotificationService
    
    context = context or {}
    results = {'success': 0, 'failed': []}
    
    for user_id in user_ids:
        try:
            user = User.objects.get(id=user_id)
            DynamicNotificationService.create(
                user=user,
                type_code=type_code,
                context=context,
                channel=channel,
                link=link
            )
            results['success'] += 1
        except Exception:
            results['failed'].append(user_id)
    
    return results


@shared_task
def send_digest_notification(user_id: int, notification_type: str = 'daily'):
    """
    Send daily/weekly digest of unread notifications
    
    Args:
        user_id: User ID to send digest to
        notification_type: Type of digest ('daily', 'weekly')
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        from django.contrib.auth.models import User
        from django.utils import timezone
        from datetime import timedelta
        
        user = User.objects.get(id=user_id)
        
        # Determine date range
        if notification_type == 'daily':
            date_from = timezone.now() - timedelta(days=1)
        elif notification_type == 'weekly':
            date_from = timezone.now() - timedelta(weeks=1)
        else:
            return False
        
        # Get unread notifications in date range
        notifications = Notification.objects.filter(
            user=user,
            is_read=False,
            created_at__gte=date_from
        ).order_by('-created_at')
        
        if not notifications.exists():
            return False
        
        # Create digest content
        subject = f"Your {notification_type} notification digest"
        message_lines = [
            f"You have {notifications.count()} unread notifications:",
            ""
        ]
        
        for notif in notifications[:10]:  # Limit to 10 most recent
            message_lines.append(f"• {notif.title}")
            message_lines.append(f"  {notif.message[:100]}...")
            message_lines.append("")
        
        if notifications.count() > 10:
            message_lines.append(f"... and {notifications.count() - 10} more")
        
        message = "\n".join(message_lines)
        
        # Send email
        from_email = getattr(settings, 'NOTIFICATION_EMAIL_FROM', settings.DEFAULT_FROM_EMAIL)
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        return True
        
    except Exception:
        return False
