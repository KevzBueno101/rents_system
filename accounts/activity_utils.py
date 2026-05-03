"""
Activity Logging Utilities

This module provides helper functions for logging user activities
across the application in a centralized, scalable manner.
"""

from django.contrib.auth.models import User
from .models import ActivityLog


def log_activity(user, action, description='', content_type='', object_id=None):
    """
    Log a user activity to the ActivityLog model.
    
    Args:
        user: User instance (can be None for system actions)
        action: Action type (must match ActivityLog.ACTION_CHOICES)
        description: Human-readable description of the action
        content_type: Model name of related object (e.g., 'Bill', 'TenantProfile')
        object_id: ID of the related object
    
    Returns:
        ActivityLog instance
    
    Example:
        log_activity(
            user=request.user,
            action='bill_generated',
            description=f'Generated bill {bill.bill_number} for {bill.tenant.full_name}',
            content_type='Bill',
            object_id=bill.id
        )
    """
    return ActivityLog.objects.create(
        user=user,
        action=action,
        description=description,
        content_type=content_type,
        object_id=object_id
    )


def get_recent_activities(limit=10, user=None, action_filter=None):
    """
    Get recent activities with optimized queries.
    
    Args:
        limit: Maximum number of activities to return
        user: Optional user to filter activities by
        action_filter: Optional action type to filter by (e.g., 'payment_recorded')
    
    Returns:
        QuerySet of ActivityLog instances
    """
    queryset = ActivityLog.objects.all()
    
    if user:
        queryset = queryset.filter(user=user)
    
    if action_filter:
        queryset = queryset.filter(action=action_filter)
    
    return queryset.order_by('-timestamp')[:limit]


def get_recent_payments(limit=10):
    """
    Get recent payment activities only.
    
    Args:
        limit: Maximum number of activities to return
    
    Returns:
        QuerySet of ActivityLog instances with payment_recorded action
    """
    return get_recent_activities(limit=limit, action_filter='payment_recorded')


def get_activity_icon(action):
    """
    Get Bootstrap icon class for a given action type.
    
    Args:
        action: Action type string
    
    Returns:
        Bootstrap icon class name
    """
    icon_map = {
        'tenant_created': 'bi-person-plus',
        'tenant_updated': 'bi-person-gear',
        'tenant_deleted': 'bi-person-x',
        'room_created': 'bi-door-open',
        'room_updated': 'bi-door-closed',
        'room_deleted': 'bi-door-closed-fill',
        'bill_generated': 'bi-file-earmark-plus',
        'bill_updated': 'bi-file-earmark-pencil',
        'bill_deleted': 'bi-file-earmark-x',
        'bill_sent': 'bi-send',
        'payment_recorded': 'bi-cash-coin',
        'payment_deleted': 'bi-cash-x',
        'admin_created': 'bi-shield-plus',
        'admin_updated': 'bi-shield-gear',
        'admin_deleted': 'bi-shield-x',
        'maintenance_created': 'bi-tools',
        'maintenance_updated': 'bi-gear',
        'maintenance_completed': 'bi-check-circle',
        'reminder_created': 'bi-bell',
        'reminder_sent': 'bi-send',
    }
    return icon_map.get(action, 'bi-activity')


def get_activity_color(action):
    """
    Get Bootstrap color class for a given action type.
    
    Args:
        action: Action type string
    
    Returns:
        Bootstrap color class (e.g., 'text-primary', 'text-success')
    """
    color_map = {
        'tenant_created': 'text-primary',
        'tenant_updated': 'text-info',
        'tenant_deleted': 'text-danger',
        'room_created': 'text-primary',
        'room_updated': 'text-info',
        'room_deleted': 'text-danger',
        'bill_generated': 'text-primary',
        'bill_updated': 'text-info',
        'bill_deleted': 'text-danger',
        'bill_sent': 'text-success',
        'payment_recorded': 'text-success',
        'payment_deleted': 'text-danger',
        'admin_created': 'text-primary',
        'admin_updated': 'text-info',
        'admin_deleted': 'text-danger',
        'maintenance_created': 'text-warning',
        'maintenance_updated': 'text-info',
        'maintenance_completed': 'text-success',
        'reminder_created': 'text-primary',
        'reminder_sent': 'text-success',
    }
    return color_map.get(action, 'text-secondary')
