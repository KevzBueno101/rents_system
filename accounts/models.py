from django.db import models
from django.contrib.auth.models import User


# ─── TENANT PROFILE ───────────────────────────────────
class TenantProfile(models.Model):
    user        = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name   = models.CharField(max_length=100)
    phone       = models.CharField(max_length=20)
    room        = models.ForeignKey('Room', on_delete=models.SET_NULL, null=True, blank=True)
    room_number = models.CharField(max_length=20, blank=True)  # legacy fallback
    photo       = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def get_room_display(self):
        if self.room:
            return self.room.room_code()
        return f"Room {self.room_number}" if self.room_number else "—"

    def __str__(self):
        return f"{self.full_name} - {self.get_room_display()}"


# ─── ADMIN PROFILE ────────────────────────────────────
class AdminProfile(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name  = models.CharField(max_length=100)
    phone      = models.CharField(max_length=20)
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


# ─── BILL ─────────────────────────────────────────────
class Bill(models.Model):
    tenant     = models.ForeignKey(TenantProfile, on_delete=models.CASCADE)
    amount     = models.DecimalField(max_digits=8, decimal_places=2)
    due_date   = models.DateField()
    is_paid    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "Paid" if self.is_paid else "Unpaid"
        return f"{self.tenant.full_name} - P{self.amount} ({status})"


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


# ─── ROOM ─────────────────────────────────────────────
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
    photo        = models.ImageField(upload_to='rooms/', blank=True, null=True)

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

    def room_code(self):
        # Fixed: use full room_number not just first char
        return f"Room {self.floor}-{self.room_number}"

    def __str__(self):
        return self.room_code()