from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Notification
from django.urls import reverse


class Command(BaseCommand):
    help = 'Create sample notifications for testing the notification system'

    def handle(self, *args, **options):
        # Get all users
        users = User.objects.all()
        
        if not users.exists():
            self.stdout.write(self.style.ERROR('No users found. Please create users first.'))
            return

        sample_notifications = [
            {
                'title': 'Welcome to RENTS System',
                'message': 'Your account has been successfully created. Explore the dashboard features.',
                'link': '/admin-dashboard/' if users.first().is_staff else '/tenant/dashboard/'
            },
            {
                'title': 'New Bill Generated',
                'message': 'A new bill has been generated for this month. Please review and make payment.',
                'link': '/billing/'
            },
            {
                'title': 'Maintenance Request Update',
                'message': 'Your maintenance request has been updated. Check the status.',
                'link': '/maintenance/'
            },
            {
                'title': 'Payment Reminder',
                'message': 'Your payment is due soon. Please settle your outstanding balance.',
                'link': '/billing/'
            },
            {
                'title': 'System Update',
                'message': 'New features have been added to the RENTS system. Check them out!',
                'link': '/admin-dashboard/'
            }
        ]

        created_count = 0
        
        for user in users:
            # Clear existing notifications for clean testing
            Notification.objects.filter(user=user).delete()
            
            # Create sample notifications for each user
            for i, notif_data in enumerate(sample_notifications[:3]):  # Create 3 notifications per user
                notification = Notification.objects.create(
                    user=user,
                    title=notif_data['title'],
                    message=notif_data['message'],
                    link=notif_data['link'],
                    is_read=(i == 0)  # Mark first notification as read
                )
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} sample notifications for {users.count()} users.')
        )
        
        # Show notification counts
        for user in users:
            total = Notification.objects.filter(user=user).count()
            unread = Notification.objects.filter(user=user, is_read=False).count()
            self.stdout.write(f'User {user.username}: {total} total, {unread} unread')
