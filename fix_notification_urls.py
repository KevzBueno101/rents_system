#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rents_system.settings')
django.setup()

from django.db import connection
from accounts.models import Notification

def fix_notification_urls():
    """Fix notification URLs from /tenant/billing/ to /tenant/bills/"""
    print("🔧 FIXING NOTIFICATION URLS")
    print("=" * 40)
    
    # Find notifications with incorrect URL
    incorrect_notifications = Notification.objects.filter(link='/tenant/billing/')
    
    print(f"\n📊 Found {incorrect_notifications.count()} notifications with incorrect URL")
    
    if incorrect_notifications.exists():
        print("\n🔧 Updating notification URLs...")
        for notif in incorrect_notifications:
            print(f"   📝 Updating: {notif.title[:50]}...")
            notif.link = '/tenant/bills/'
            notif.save()
        
        print(f"   ✅ Updated {incorrect_notifications.count()} notifications")
    else:
        print("   ✅ No notifications with incorrect URL found")
    
    # Verify the fix
    remaining_incorrect = Notification.objects.filter(link='/tenant/billing/').count()
    print(f"\n✅ Verification: {remaining_incorrect} notifications still have incorrect URL")
    
    # Show current notification URLs
    print("\n📋 Current notification URLs:")
    unique_links = Notification.objects.values_list('link', flat=True).distinct()
    for link in sorted(unique_links):
        if link:  # Skip empty links
            count = Notification.objects.filter(link=link).count()
            print(f"   🔗 {link} ({count} notifications)")
    
    print("\n🎉 NOTIFICATION URL FIX COMPLETE!")

if __name__ == "__main__":
    fix_notification_urls()
