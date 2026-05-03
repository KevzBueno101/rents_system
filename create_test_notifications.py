#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rents_system.settings')
django.setup()

from accounts.models import Notification
from django.contrib.auth.models import User
from accounts.services.notification_service import NotificationService

# Get first admin user
admin_user = User.objects.filter(is_staff=True).first()
if admin_user:
    # Create 10 test notifications
    for i in range(10):
        NotificationService.create_notification(
            user=admin_user,
            title=f'Test Notification {i+1}',
            message=f'This is test notification number {i+1} to test scrolling functionality.',
            notif_type='system'
        )
    print(f'Created 10 test notifications for {admin_user.username}')
else:
    print('No admin user found')
