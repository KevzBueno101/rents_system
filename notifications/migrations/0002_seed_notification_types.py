"""Seed notification types from existing NOTIFICATION_TYPES"""

from django.db import migrations


def seed_notification_types(apps, schema_editor):
    """Seed NotificationType table with existing static types"""
    NotificationType = apps.get_model('notifications', 'NotificationType')
    
    # Map existing static types to dynamic types
    type_mapping = {
        'payment': 'Payment',
        'billing': 'Billing',
        'maintenance': 'Maintenance',
        'announcement': 'Announcement',
        'system': 'System',
        'reminder': 'Reminder',
        'payment_proof': 'Payment Proof',
    }
    
    # Create NotificationType entries for each existing type
    for type_code, label in type_mapping.items():
        NotificationType.objects.update_or_create(
            code=type_code,
            label=label,
            defaults={
                'icon': f'bi-{type_code.replace("_", "-")}-circle',
                'color': 'primary' if type_code in ['payment', 'billing'] else 'info',
                'is_active': True,
            }
        )
    
    print(f"Seeded {len(type_mapping)} notification types")


def reverse_seed_notification_types(apps, schema_editor):
    """Reverse the seeding by deleting created notification types"""
    NotificationType = apps.get_model('notifications', 'NotificationType')
    
    # Delete the seeded types
    type_codes = ['payment', 'billing', 'maintenance', 'announcement', 'system', 'reminder', 'payment_proof']
    NotificationType.objects.filter(code__in=type_codes).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_notification_types, reverse_seed_notification_types)
    ]
