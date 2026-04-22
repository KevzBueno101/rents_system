from django.db import models
from django.contrib.auth.models import User


# ─── TENANT PROFILE ───────────────────────────────────
class TenantProfile(models.Model):
    user        = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name   = models.CharField(max_length=100)
    phone       = models.CharField(max_length=20)
    room_number = models.CharField(max_length=20)
    photo       = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - Room {self.room_number}"

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


# ─── ROOM ─────────────────────────────────────────────
class Room(models.Model):
    room_number  = models.CharField(max_length=20, unique=True)
    capacity     = models.PositiveIntegerField(default=1)
    monthly_rate = models.DecimalField(max_digits=8, decimal_places=2)
    photo        = models.ImageField(upload_to='rooms/', blank=True, null=True)  # ← NEW

    def occupied_beds(self):
        return TenantProfile.objects.filter(room_number=self.room_number).count()

    def is_full(self):
        return self.occupied_beds() >= self.capacity

    def status(self):
        return "Occupied" if self.is_full() else "Vacant"

    def get_tenants(self):
        return TenantProfile.objects.filter(room_number=self.room_number)

    def __str__(self):
        return f"Room {self.room_number} ({self.status()})"
# ─── BILL ─────────────────────────────────────────────
class Bill(models.Model):
    tenant     = models.ForeignKey(TenantProfile, on_delete=models.CASCADE)
    amount     = models.DecimalField(max_digits=8, decimal_places=2)
    due_date   = models.DateField()
    is_paid    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "Paid" if self.is_paid else "Unpaid"
        return f"{self.tenant.full_name} - ₱{self.amount} ({status})"


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

class Room(models.Model):
    room_number  = models.CharField(max_length=20, unique=True)
    floor        = models.PositiveIntegerField(default=1)
    capacity     = models.PositiveIntegerField(default=1)
    monthly_rate = models.DecimalField(max_digits=8, decimal_places=2)
    photo        = models.ImageField(upload_to='rooms/', blank=True, null=True)

    def occupied_beds(self):
        return TenantProfile.objects.filter(room_number=self.room_number).count()

    def is_full(self):
        return self.occupied_beds() >= self.capacity

    def status(self):
        return "Occupied" if self.is_full() else "Vacant"

    def get_tenants(self):
        return TenantProfile.objects.filter(room_number=self.room_number)

    def room_code(self):
        return f"Room {self.floor}-{self.room_number}"

    def __str__(self):
        return self.room_code()