"""
URL configuration for dynamic notification system

Defines URL patterns for notification views, API endpoints,
and WebSocket connections.
"""

from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Existing endpoints - preserve backward compatibility
    path('mark-read/<int:pk>/', views.mark_notification_read, name='notification_mark_read'),
    
    # New endpoints
    path('', views.NotificationCenterView.as_view(), name='notification_center'),
    path('preferences/', views.NotificationPreferencesView.as_view(), name='notification_preferences'),
    path('bulk-action/', views.bulk_action, name='notification_bulk_action'),
    path('stream/', views.notification_stream, name='notification_stream'),
    path('badge/', views.notification_badge, name='notification_badge'),
    path('stats/', views.notification_stats, name='notification_stats'),
    path('mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('delete/<int:pk>/', views.delete_notification, name='delete_notification'),
]
