from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from pathlib import Path
from django.utils import timezone


PHONE_VALIDATOR = RegexValidator(
    regex=r'^\d{10,15}$',
    message='Phone number must contain only digits (10-15 numbers).'
)


# ─── TENANT PROFILE ───────────────────────────────────
class TenantProfile(models.Model):
    user        = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name   = models.CharField(max_length=100)
    phone       = models.CharField(max_length=20, validators=[PHONE_VALIDATOR])
    room        = models.ForeignKey('Room', on_delete=models.PROTECT, null=True, blank=True)
    room_number = models.CharField(max_length=20, blank=True)  # legacy fallback
    photo       = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def get_room_display(self):
        if self.room:
            return self.room.room_code
        return f"Room {self.room_number}" if self.room_number else "—"

    def __str__(self):
        return f"{self.full_name} - {self.get_room_display()}"


# ─── ADMIN PROFILE ────────────────────────────────────
class AdminProfile(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name  = models.CharField(max_length=100)
    phone      = models.CharField(max_length=20, validators=[PHONE_VALIDATOR])
    created_at = models.DateTimeField(auto_now_add=True)
    photo      = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='admins_created'
    )

    def __str__(self):
        return f"{self.full_name} (Admin)"


# ─── MAINTENANCE REPORT ───────────────────────────────
class MaintenanceReport(models.Model):
    STATUS_CHOICES = [
        ('open',      'Open'),
        ('ongoing',   'Ongoing'),
        ('completed', 'Completed'),
    ]
    tenant      = models.ForeignKey(TenantProfile, on_delete=models.CASCADE)
    description = models.TextField()
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tenant.full_name} - {self.status}"


# ─── VIOLATION ────────────────────────────────────────
class Violation(models.Model):
    tenant      = models.ForeignKey(TenantProfile, on_delete=models.CASCADE)
    description = models.TextField()
    date        = models.DateField()
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tenant.full_name} - {self.date}"


# ─── INCLUSION ───────────────────────────────────────
class Inclusion(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


# ─── APPLIANCE ───────────────────────────────────────
class Appliance(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


# ─── ROOM UPLOAD PATH FUNCTIONS ───────────────────────────────
def room_primary_upload_path(instance, filename):
    """Generate upload path for a room's primary image."""
    if instance and hasattr(instance, 'get_primary_image_path'):
        return instance.get_primary_image_path(filename)
    return f'rooms/{filename}'

def room_additional_upload_path(instance, filename):
    """Generate upload path for a room's additional image."""
    if instance and getattr(instance, 'room', None):
        return instance.room.get_additional_image_path(instance.order, filename)
    return f'room_images/{filename}'

# ─── ROOM MODEL ────────────────────────────────────────────
class Room(models.Model):

    BED_CHOICES = [
        ('single',      'Single'),
        ('double_deck', 'Double Deck'),
        ('both',        'Both'),
    ]

    # ── BASIC ─────────────────────────────────────────
    room_number  = models.CharField(max_length=20)
    floor        = models.PositiveIntegerField(default=1)
    capacity     = models.PositiveIntegerField(default=1)
    monthly_rate = models.DecimalField(max_digits=8, decimal_places=2)
    photo        = models.ImageField(upload_to=room_primary_upload_path, blank=True, null=True)

    # ── ROOM FEATURES ─────────────────────────────────
    area       = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    num_cr     = models.PositiveIntegerField(default=1)
    bed_type   = models.CharField(max_length=20, choices=BED_CHOICES, default='single')
    has_lababo = models.BooleanField(default=False)  # Sink

    # ── INCLUSIONS ────────────────────────────────────
    water_included       = models.BooleanField(default=False)
    electricity_included = models.BooleanField(default=False)
    has_wifi             = models.BooleanField(default=False)
    dynamic_inclusions   = models.ManyToManyField(Inclusion, blank=True)

    def occupied_beds(self):
        return TenantProfile.objects.filter(room=self).count()

    def available_beds(self):
        return self.capacity - self.occupied_beds()

    def is_full(self):
        return self.occupied_beds() >= self.capacity

    def status(self):
        return "Occupied" if self.is_full() else "Vacant"

    def get_tenants(self):
        return TenantProfile.objects.filter(room=self)

    @property          
    def room_code(self):
        return f"Room {self.floor}-{self.room_number}"
    
    def get_room_directory_path(self):
        """Generate safe directory path for room media storage"""
        # Convert room code to safe directory name
        safe_name = f"Room_{self.floor}-{self.room_number}"
        # Remove any unsafe characters and replace spaces with underscores
        safe_name = ''.join(c if c.isalnum() or c in '-_' else '_' for c in safe_name)
        return f"rooms/{safe_name}"
    
    def get_primary_image_path(self, filename="primary.jpg"):
        """Get the path for primary room image"""
        return f"{self.get_room_directory_path()}/primary.jpg"
    
    def get_additional_image_path(self, index, filename="image.jpg"):
        """Get the path for additional room image"""
        return f"{self.get_room_directory_path()}/{index}.jpg"
    
    @property
    def all_images(self):
        """Unified image source combining primary photo and additional images with proper ordering"""
        images = []
        
        # Add primary photo first (order 0)
        if self.photo:
            images.append({
                'url': self.photo.url,
                'order': 0,
                'is_primary': True,
                'filename': Path(self.photo.name).name,
                'type': 'primary'
            })
        
        # Add additional images in order (order 1, 2, 3, ...)
        for img in self.additional_images.all().order_by('order', 'id'):
            if not img.image:
                continue
            images.append({
                'url': img.image.url,
                'order': img.order,
                'is_primary': False,
                'filename': Path(img.image.name).name,
                'type': 'additional',
                'image_id': img.id
            })
        
        return images
    
    @property
    def image_count(self):
        """Get total number of images for this room"""
        return len(self.all_images)
    
    @property
    def primary_image(self):
        """Get primary image URL or first additional image"""
        images = self.all_images
        return images[0]['url'] if images else None
    
    def __str__(self):
        return self.room_code


# ─── ROOM IMAGE ─────────────────────────────────────────
class RoomImage(models.Model):
    """Additional images for rooms with ordering support"""
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to=room_additional_upload_path)
    order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Room Image'
        verbose_name_plural = 'Room Images'
        indexes = [
            models.Index(fields=['room', 'order'], name='idx_room_image_order'),
        ]
    
    @classmethod
    def get_upload_path(cls, instance, filename):
        """Generate upload path for additional room images"""
        if instance and getattr(instance, 'room', None):
            return instance.room.get_additional_image_path(instance.order, filename)
        return f'room_images/{filename}'
    
    def __str__(self):
        return f"{self.room.room_code} - Image {self.order}"


# ─── BILLING SYSTEM ─────────────────────────────────────

class Bill(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]

    tenant = models.ForeignKey(TenantProfile, on_delete=models.CASCADE, related_name='bills')
    room = models.ForeignKey('Room', on_delete=models.SET_NULL, null=True, blank=True, related_name='bills')
    bill_number = models.CharField(max_length=30, unique=True, null=True, blank=True)

    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.bill_number} - {self.tenant.full_name}"

    def save(self, *args, **kwargs):
        if not self.bill_number:
            self.bill_number = self.generate_bill_number()
        if self.room is None and self.tenant.room:
            self.room = self.tenant.room
        super().save(*args, **kwargs)

    def generate_bill_number(self):
        from django.db.models import Max
        year = self.period_start.year
        prefix = f"BILL-{year}"
        last_bill = Bill.objects.filter(bill_number__startswith=prefix).aggregate(
            max_num=Max('bill_number')
        )['max_num']
        if last_bill:
            last_num = int(last_bill.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        return f"{prefix}-{new_num:05d}"

    @property
    def paid_amount(self):
        return self.payments.aggregate(total=models.Sum('amount'))['total'] or 0

    @property
    def balance(self):
        return self.total_amount - self.paid_amount

    def update_status(self):
        from django.utils import timezone
        today = timezone.now().date()

        if self.balance <= 0:
            self.status = 'paid'
        elif self.paid_amount > 0:
            self.status = 'partial'
        elif self.due_date < today and self.balance > 0:
            self.status = 'overdue'
        elif self.status == 'draft':
            pass  # Keep draft status
        else:
            self.status = 'sent'
        self.save(update_fields=['status'])


class BillItem(models.Model):
    bill = models.ForeignKey(Bill, related_name='items', on_delete=models.CASCADE)
    description = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.description} - P{self.amount}"


class Payment(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('gcash', 'GCash'),
        ('maya', 'Maya'),
        ('other', 'Other'),
    ]

    bill = models.ForeignKey(Bill, related_name='payments', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHODS)
    reference_number = models.CharField(max_length=50, blank=True)
    proof = models.ImageField(upload_to='payments/', blank=True, null=True)
    receipt_id = models.CharField(max_length=80, unique=True, blank=True, null=True)
    receipt_image = models.ImageField(
        upload_to='receipts/', 
        blank=True, 
        null=True
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"P{self.amount} - {self.bill.bill_number}"


# ─── ACTIVITY LOG ─────────────────────────────────────
class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('tenant_created', 'Tenant Created'),
        ('tenant_updated', 'Tenant Updated'),
        ('tenant_deleted', 'Tenant Deleted'),
        ('room_created', 'Room Created'),
        ('room_updated', 'Room Updated'),
        ('room_deleted', 'Room Deleted'),
        ('bill_generated', 'Bill Generated'),
        ('bill_updated', 'Bill Updated'),
        ('bill_deleted', 'Bill Deleted'),
        ('bill_sent', 'Bill Sent'),
        ('payment_recorded', 'Payment Recorded'),
        ('payment_deleted', 'Payment Deleted'),
        ('payment_proof_uploaded', 'Payment Proof Uploaded'),
        ('admin_created', 'Admin Created'),
        ('admin_updated', 'Admin Updated'),
        ('admin_deleted', 'Admin Deleted'),
        ('maintenance_created', 'Maintenance Created'),
        ('maintenance_updated', 'Maintenance Updated'),
        ('maintenance_completed', 'Maintenance Completed'),
        ('reminder_created', 'Reminder Created'),
        ('reminder_sent', 'Reminder Sent'),
        ('rule_created', 'Rule Created'),
        ('rule_deleted', 'Rule Deleted'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='activities')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField(blank=True)
    
    # Flexible references for related objects
    content_type = models.CharField(max_length=100, blank=True, help_text='Model name (e.g., Bill, TenantProfile)')
    object_id = models.IntegerField(null=True, blank=True, help_text='ID of the related object')
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        indexes = [
            models.Index(fields=['user'], name='idx_activity_user'),
            models.Index(fields=['action'], name='idx_activity_action'),
            models.Index(fields=['timestamp'], name='idx_activity_timestamp'),
            models.Index(fields=['content_type'], name='idx_activity_content_type'),
            models.Index(fields=['-timestamp'], name='idx_activity_timestamp_desc'),
            models.Index(fields=['user', '-timestamp'], name='idx_activity_user_timestamp'),
            models.Index(fields=['action', '-timestamp'], name='idx_activity_action_timestamp'),
        ]
    
    def __str__(self):
        user_str = self.user.username if self.user else 'System'
        return f"{user_str} - {self.get_action_display()} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
    
    def get_time_ago(self):
        """Return human-readable time ago string"""
        from django.utils.timesince import timesince
        return timesince(self.timestamp) + ' ago'


# ─── NOTIFICATION ─────────────────────────────────────
class Notification(models.Model):
    """Production-ready notification model for tenant-specific system alerts"""
    
    NOTIFICATION_TYPES = [
        ('payment', 'Payment'),
        ('billing', 'Billing'),
        ('maintenance', 'Maintenance'),
        ('announcement', 'Announcement'),
        ('system', 'System'),
        ('reminder', 'Reminder'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True, help_text='Internal URL path for redirection')
    type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        indexes = [
            models.Index(fields=['user', '-created_at'], name='idx_notification_user_created'),
            models.Index(fields=['user', 'is_read'], name='idx_notification_user_read'),
            models.Index(fields=['type'], name='idx_notification_type'),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def get_absolute_url(self):
        """Get the absolute URL for this notification"""
        if self.link:
            return self.link
        return '/tenant/dashboard/'


# ─── TENANT REMINDER ───────────────────────────────────
class TenantReminder(models.Model):
    """Reminders sent to tenants (cleanliness, rules, etc.) with scheduling support"""
    REMINDER_TYPES = [
        ('cleanliness', 'Cleanliness'),
        ('rules', 'House Rules'),
        ('payment', 'Payment Reminder'),
        ('general', 'General'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('read', 'Read'),
    ]

    tenant = models.ForeignKey(TenantProfile, on_delete=models.CASCADE, related_name='reminders')
    title = models.CharField(max_length=255)
    message = models.TextField()
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPES, default='general')
    
    # Scheduling fields
    scheduled_at = models.DateTimeField(null=True, blank=True, help_text='Optional: Schedule for future delivery')
    is_sent = models.BooleanField(default=False)
    
    # Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Tenant Reminder'
        verbose_name_plural = 'Tenant Reminders'

    def __str__(self):
        return f"{self.tenant.full_name} - {self.title}"

    def mark_as_sent(self):
        """Mark reminder as sent and create notification"""
        from django.utils import timezone
        self.is_sent = True
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save(update_fields=['is_sent', 'status', 'sent_at'])
        
        # Create notification for tenant
        Notification.objects.create(
            user=self.tenant.user,
            title=self.title,
            message=self.message
        )


# ─── RULE ──────────────────────────────────────────────
class Rule(models.Model):
    """Global rules managed by admin, viewable by tenants"""
    title = models.CharField(max_length=255)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Rule'
        verbose_name_plural = 'Rules'

    def __str__(self):
        return self.title

    @property
    def status_display(self):
        return 'Active' if self.is_active else 'Inactive'
