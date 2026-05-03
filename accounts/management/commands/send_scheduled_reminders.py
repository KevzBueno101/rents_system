from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import TenantReminder


class Command(BaseCommand):
    help = 'Send scheduled reminders whose time has arrived'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Find reminders that are:
        # - Not yet sent (is_sent=False)
        # - Have a scheduled time (scheduled_at is not null)
        # - Scheduled time is now or in the past (scheduled_at <= now)
        pending_reminders = TenantReminder.objects.filter(
            is_sent=False,
            scheduled_at__isnull=False,
            scheduled_at__lte=now,
            status='pending'
        )
        
        count = 0
        for reminder in pending_reminders:
            try:
                reminder.mark_as_sent()
                count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Sent reminder "{reminder.title}" to {reminder.tenant.full_name}'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Failed to send reminder {reminder.id}: {str(e)}'
                    )
                )
        
        if count == 0:
            self.stdout.write('No scheduled reminders to send.')
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully sent {count} reminder(s).')
            )
