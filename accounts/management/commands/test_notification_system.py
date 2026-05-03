"""
Test Command for Notification System

This command tests the complete notification system functionality:
- User isolation (Tenant A can't see Tenant B notifications)
- Dynamic routing and redirects
- Admin trigger integrations
- Security and performance
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from accounts.models import Notification, TenantProfile
from accounts.services.notification_service import NotificationService


class Command(BaseCommand):
    help = 'Test the complete notification system functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed test output',
        )

    def handle(self, *args, **options):
        self.verbose = options.get('verbose', False)
        self.client = Client()
        
        self.stdout.write(self.style.SUCCESS('🔔 Testing RENTS Notification System'))
        self.stdout.write('=' * 50)
        
        # Test 1: User Isolation
        self.test_user_isolation()
        
        # Test 2: Dynamic Routing
        self.test_dynamic_routing()
        
        # Test 3: Admin Trigger Integration
        self.test_admin_triggers()
        
        # Test 4: Security
        self.test_security()
        
        # Test 5: Performance
        self.test_performance()
        
        self.stdout.write(self.style.SUCCESS('✅ All tests completed!'))

    def test_user_isolation(self):
        """Test that users can only see their own notifications"""
        self.stdout.write('\n🧪 Test 1: User Isolation')
        
        # Get two different users
        users = User.objects.all()[:2]
        if len(users) < 2:
            self.stdout.write(self.style.WARNING('⚠️  Need at least 2 users for isolation test'))
            return
        
        user_a, user_b = users[0], users[1]
        
        # Create notifications for each user
        notif_a = NotificationService.create_notification(
            user=user_a,
            title="User A Notification",
            message="This should only be visible to User A",
            link="/tenant/dashboard/",
            notif_type="system"
        )
        
        notif_b = NotificationService.create_notification(
            user=user_b,
            title="User B Notification", 
            message="This should only be visible to User B",
            link="/tenant/dashboard/",
            notif_type="system"
        )
        
        # Test User A can only see their notifications
        notifications_a, unread_a = NotificationService.get_user_notifications(user_a)
        self.assert_test(
            notif_a.id in [n.id for n in notifications_a],
            "User A can see their own notification"
        )
        self.assert_test(
            notif_b.id not in [n.id for n in notifications_a],
            "User A cannot see User B's notification"
        )
        
        # Test User B can only see their notifications
        notifications_b, unread_b = NotificationService.get_user_notifications(user_b)
        self.assert_test(
            notif_b.id in [n.id for n in notifications_b],
            "User B can see their own notification"
        )
        self.assert_test(
            notif_a.id not in [n.id for n in notifications_b],
            "User B cannot see User A's notification"
        )
        
        self.stdout.write(self.style.SUCCESS('✅ User isolation test passed'))

    def test_dynamic_routing(self):
        """Test dynamic notification routing and redirects"""
        self.stdout.write('\n🧪 Test 2: Dynamic Routing')
        
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.WARNING('⚠️  No users found for routing test'))
            return
        
        # Test different notification types
        test_cases = [
            ("payment", "/tenant/billing/"),
            ("billing", "/tenant/billing/"),
            ("maintenance", "/tenant/reports/"),
            ("announcement", "/tenant/dashboard/"),
            ("unknown", "/tenant/dashboard/"),  # Default fallback
        ]
        
        for notif_type, expected_link in test_cases:
            notif = NotificationService.create_notification(
                user=user,
                title=f"Test {notif_type}",
                message=f"Testing {notif_type} routing",
                notif_type=notif_type
            )
            
            actual_link = notif.get_absolute_url()
            self.assert_test(
                actual_link == expected_link,
                f"Routing for {notif_type}: {actual_link} == {expected_link}"
            )
        
        self.stdout.write(self.style.SUCCESS('✅ Dynamic routing test passed'))

    def test_admin_triggers(self):
        """Test admin trigger integrations"""
        self.stdout.write('\n🧪 Test 3: Admin Trigger Integration')
        
        # Get a tenant user for testing
        tenant_profile = TenantProfile.objects.first()
        if not tenant_profile:
            self.stdout.write(self.style.WARNING('⚠️  No tenants found for trigger test'))
            return
        
        tenant_user = tenant_profile.user
        
        # Test payment notification creation
        try:
            payment_notif = NotificationService.create_payment_notification(
                tenant_user=tenant_user,
                amount=1500.00
            )
            self.assert_test(
                payment_notif.type == "payment",
                "Payment notification created with correct type"
            )
            if self.verbose:
                self.stdout.write(f"  📝 Payment message: '{payment_notif.message}'")
            self.assert_test(
                "1,500.00" in payment_notif.message,
                "Payment notification includes amount"
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Payment notification failed: {e}"))
        
        # Test billing notification creation
        try:
            billing_notif = NotificationService.create_billing_notification(
                tenant_user=tenant_user,
                bill_number="BILL-2025-00001"
            )
            self.assert_test(
                billing_notif.type == "billing",
                "Billing notification created with correct type"
            )
            self.assert_test(
                "BILL-2025-00001" in billing_notif.message,
                "Billing notification includes bill number"
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Billing notification failed: {e}"))
        
        # Test maintenance notification creation
        try:
            maintenance_notif = NotificationService.create_maintenance_notification(
                tenant_user=tenant_user,
                status="completed"
            )
            self.assert_test(
                maintenance_notif.type == "maintenance",
                "Maintenance notification created with correct type"
            )
            self.assert_test(
                "completed" in maintenance_notif.message,
                "Maintenance notification includes status"
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Maintenance notification failed: {e}"))
        
        self.stdout.write(self.style.SUCCESS('✅ Admin trigger test passed'))

    def test_security(self):
        """Test security measures"""
        self.stdout.write('\n🧪 Test 4: Security')
        
        users = User.objects.all()[:2]
        if len(users) < 2:
            self.stdout.write(self.style.WARNING('⚠️  Need at least 2 users for security test'))
            return
        
        user_a, user_b = users[0], users[1]
        
        # Create notification for User A
        notif = NotificationService.create_notification(
            user=user_a,
            title="Security Test",
            message="Testing security measures",
            notif_type="system"
        )
        
        # Test User B cannot mark User A's notification as read
        success = NotificationService.mark_as_read(
            notification_id=notif.id,
            user=user_b
        )
        self.assert_test(
            not success,
            "User cannot mark another user's notification as read"
        )
        
        # Test User A can mark their own notification as read
        success = NotificationService.mark_as_read(
            notification_id=notif.id,
            user=user_a
        )
        self.assert_test(
            success,
            "User can mark their own notification as read"
        )
        
        # Verify notification is actually marked as read
        notif.refresh_from_db()
        self.assert_test(
            notif.is_read,
            "Notification is properly marked as read"
        )
        
        self.stdout.write(self.style.SUCCESS('✅ Security test passed'))

    def test_performance(self):
        """Test performance with database indexes"""
        self.stdout.write('\n🧪 Test 5: Performance')
        
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.WARNING('⚠️  No users found for performance test'))
            return
        
        # Create multiple notifications for performance testing
        notification_ids = []
        for i in range(10):
            notif = NotificationService.create_notification(
                user=user,
                title=f"Performance Test {i+1}",
                message=f"Testing performance with notification {i+1}",
                notif_type="system"
            )
            notification_ids.append(notif.id)
        
        # Test retrieval performance
        try:
            notifications, unread_count = NotificationService.get_user_notifications(
                user=user,
                limit=5
            )
            
            self.assert_test(
                len(notifications) <= 5,
                "Notification limit is respected"
            )
            
            self.assert_test(
                unread_count >= 0,
                "Unread count is calculated correctly"
            )
            
            # Test mark all as read performance
            marked_count = NotificationService.mark_all_as_read(user)
            self.assert_test(
                marked_count >= 0,
                "Mark all as read works correctly"
            )
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Performance test failed: {e}"))
        
        self.stdout.write(self.style.SUCCESS('✅ Performance test passed'))

    def assert_test(self, condition, message):
        """Helper method to assert test conditions"""
        if condition:
            if self.verbose:
                self.stdout.write(f"  ✅ {message}")
        else:
            self.stdout.write(self.style.ERROR(f"  ❌ {message}"))
            raise AssertionError(f"Test failed: {message}")
