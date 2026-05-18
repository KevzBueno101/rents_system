"""
Django app configuration for notifications system
"""

from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'
    verbose_name = 'Dynamic Notifications'
    
    def ready(self):
        """Import signals when app is ready"""
        try:
            from . import signals
        except ImportError:
            # Signals module not created yet
            pass
