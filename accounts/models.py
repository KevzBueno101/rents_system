from django.db import models
from django.contrib.auth.models import User

class TenantProfile(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name  = models.CharField(max_length=100)
    phone      = models.CharField(max_length=20)
    room_number= models.CharField(max_length=20)
    created_at  = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.full_name} - Room {self.room_number}"