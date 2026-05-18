"""
Dynamic Notification Models

This module extends the existing notification system with support for:
- Dynamic notification types
- Admin-manageable notification templates
- User notification preferences
"""

from django.db import models
from django.conf import settings


class NotificationType(models.Model):
    """Dynamic notification types that can be created by admins"""
    
    code = models.SlugField(
        unique=True, 
        max_length=60, 
        help_text="Unique code for this notification type"
    )
    label = models.CharField(
        max_length=100, 
        help_text="Human-readable name for this notification type"
    )
    description = models.TextField(
        blank=True, 
        help_text="Description of when this notification type is used"
    )
    icon = models.CharField(
        max_length=50, 
        blank=True, 
        help_text="CSS icon class or name (e.g., 'bi-info-circle')"
    )
    color = models.CharField(
        max_length=20, 
        blank=True, 
        help_text="Bootstrap color class (e.g., 'success')"
    )
    is_active = models.BooleanField(
        default=True, 
        help_text="Whether this notification type can be used"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['label']
        verbose_name = 'Notification Type'
        verbose_name_plural = 'Notification Types'

    def __str__(self):
        return self.label


class NotificationTemplate(models.Model):
    """Admin-manageable notification templates with variable substitution"""
    
    notification_type = models.ForeignKey(
        NotificationType, 
        on_delete=models.CASCADE, 
        related_name='templates'
    )
    language = models.CharField(
        max_length=10, 
        default='en'
    )
    title_template = models.CharField(
        max_length=255,
        help_text="Use {{ variable_name }} for substitution. E.g., 'New message from {{ sender }}'"
    )
    body_template = models.TextField(
        help_text="Supports {{ variable_name }} substitution."
    )
    is_default = models.BooleanField(
        default=False,
        help_text="Whether this is the default template for this notification type"
    )
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('notification_type', 'language')]
        verbose_name = 'Notification Template'
        verbose_name_plural = 'Notification Templates'

    def __str__(self):
        return f"{self.notification_type.label} ({self.language})"


class UserNotificationPreference(models.Model):
    """Per-user notification delivery preferences"""
    
    CHANNEL_CHOICES = [
        ('in_app', 'In-App Only'),
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('all', 'All Channels'),
        ('none', 'Disabled'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='notification_preference'
    )
    default_channel = models.CharField(
        max_length=20, 
        choices=CHANNEL_CHOICES, 
        default='in_app'
    )
    # Per-type overrides stored as JSON: {"payment": "email", "reminder": "sms"}
    type_overrides = models.JSONField(
        default=dict, 
        blank=True, 
        help_text="Per-type channel overrides for this user"
    )
    quiet_hours_start = models.TimeField(
        null=True, 
        blank=True, 
        help_text="Start time when user should not receive notifications"
    )
    quiet_hours_end = models.TimeField(
        null=True, 
        blank=True, 
        help_text="End time when user should not receive notifications"
    )
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'User Notification Preference'

    def __str__(self):
        return f"{self.user.username}'s preferences"
