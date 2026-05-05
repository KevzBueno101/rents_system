"""
User Service Layer - Centralized business logic for user operations.
Provides single source of truth for username validation and user management.
"""

from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import transaction
from ..activity_utils import log_activity


class UserService:
    """Service layer for user-related operations with robust validation."""
    
    @staticmethod
    def validate_username(username, exclude_user_id=None):
        """
        Validate username with case-insensitive uniqueness check.
        
        Args:
            username (str): Username to validate
            exclude_user_id (int, optional): User ID to exclude from check (for updates)
            
        Returns:
            str: Validated username
            
        Raises:
            ValidationError: If username is invalid or already exists
        """
        if not username:
            raise ValidationError("Username is required.")
        
        if len(username.strip()) < 3:
            raise ValidationError("Username must be at least 3 characters long.")
        
        # Check for invalid characters
        if not username.replace('_', '').replace('-', '').isalnum():
            raise ValidationError("Username can only contain letters, numbers, underscores, and hyphens.")
        
        # Case-insensitive uniqueness check
        queryset = User.objects.filter(username__iexact=username.strip())
        if exclude_user_id:
            queryset = queryset.exclude(id=exclude_user_id)
            
        if queryset.exists():
            raise ValidationError("Username already exists. Please choose a different one.")
        
        return username.strip()
    
    
    @staticmethod
    @transaction.atomic
    def update_username(user, new_username, request=None):
        old_username = user.username
        
        validated_username = UserService.validate_username(
            new_username, 
            exclude_user_id=user.id
        )
        
        if old_username == validated_username:
            return user
        
        user.username = validated_username
        user.save()
        
        # Fixed: removed invalid 'request' kwarg, fixed action to valid choice
        log_activity(
            user=user,
            action='tenant_updated',  # ← valid ACTION_CHOICES value
            description=f'Username changed from "{old_username}" to "{validated_username}"',
            content_type='User',
            object_id=user.id
        )
        
        return user
        """
        Update user username with validation and logging.
        
        Args:
            user (User): User instance to update
            new_username (str): New username
            request (HttpRequest, optional): Request object for logging
            
        Returns:
            User: Updated user instance
            
        Raises:
            ValidationError: If new username is invalid
        """
        old_username = user.username
        
        # Validate new username
        validated_username = UserService.validate_username(new_username, exclude_user_id=user.id)
        
        # Only update if username actually changed
        if old_username == validated_username:
            return user
        
        # Update username
        user.username = validated_username
        user.save()
        
        # Log the change if request is available
        if request:
            log_activity(
                user=user,
                action='username_changed',
                description=f'Username changed from "{old_username}" to "{validated_username}"',
                content_type='User',
                object_id=user.id,
                request=request
            )
        
        return user
    
    @staticmethod
    def create_user_with_validation(username, email, password, **kwargs):
        """
        Create new user with robust validation.
        
        Args:
            username (str): Username for new user
            email (str): Email for new user
            password (str): Password for new user
            **kwargs: Additional user fields
            
        Returns:
            User: Created user instance
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate username (no exclude_user_id for new users)
        validated_username = UserService.validate_username(username)
        
        # Check email uniqueness
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Email is already registered.")
        
        # Create user
        user = User.objects.create_user(
            username=validated_username,
            email=email,
            password=password,
            **kwargs
        )
        
        return user
    
    @staticmethod
    def is_username_available(username, exclude_user_id=None):
        """
        Check if username is available (case-insensitive).
        
        Args:
            username (str): Username to check
            exclude_user_id (int, optional): User ID to exclude from check
            
        Returns:
            bool: True if available, False if taken
        """
        try:
            UserService.validate_username(username, exclude_user_id)
            return True
        except ValidationError:
            return False
