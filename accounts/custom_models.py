"""
Custom User Model with enhanced validation.
Extends Django's AbstractUser for better control over authentication.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """
    Custom User model with enhanced username validation.
    Inherits from AbstractUser to maintain Django auth compatibility.
    """
    
    # Override username field with custom validation
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits, underscores, and hyphens only.'),
        validators=[],
        error_messages={
            'unique': _('A user with that username already exists.'),
        },
    )
    
    class Meta:
        db_table = 'auth_custom_user'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
    
    def clean(self):
        """Model-level validation for username."""
        super().clean()
        
        if self.username:
            # Case-insensitive uniqueness check
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            queryset = User.objects.filter(username__iexact=self.username.strip())
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            
            if queryset.exists():
                raise ValidationError({
                    'username': _('Username already exists (case-insensitive).')
                })
            
            # Character validation
            if not self.username.replace('_', '').replace('-', '').isalnum():
                raise ValidationError({
                    'username': _('Username can only contain letters, numbers, underscores, and hyphens.')
                })
    
    def save(self, *args, **kwargs):
        """Override save to ensure validation runs."""
        self.full_clean()
        super().save(*args, **kwargs)


# For backward compatibility, we'll use Django's default User
# but add validation through the service layer
User = None  # This will be imported from django.contrib.auth
