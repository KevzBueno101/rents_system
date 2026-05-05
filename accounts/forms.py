from django import forms
from django.forms import formset_factory
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Bill, BillItem, Payment, TenantProfile, TenantReminder
from django.utils import timezone
from .services.user_service import UserService


class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['tenant', 'period_start', 'period_end', 'due_date', 'total_amount', 'notes', 'status']
        widgets = {
            'tenant': forms.Select(attrs={'class': 'form-select'}),
            'period_start': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'period_end': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tenant'].queryset = TenantProfile.objects.select_related('user', 'room').order_by('full_name')


class BillItemForm(forms.ModelForm):
    class Meta:
        model = BillItem
        fields = ['description', 'amount']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item description'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
        }


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_date', 'payment_method', 'reference_number', 'proof', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reference # (optional)'}),
            'proof': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Notes (optional)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_date'].initial = timezone.now().date()


BillItemFormSet = formset_factory(BillItemForm, extra=1, can_delete=True)


class TenantReminderForm(forms.ModelForm):
    """Form for creating tenant reminders with optional scheduling"""
    class Meta:
        model = TenantReminder
        fields = ['tenant', 'title', 'message', 'reminder_type', 'scheduled_at']
        widgets = {
            'tenant': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reminder title'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Reminder message'}),
            'reminder_type': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_at': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tenant'].queryset = TenantProfile.objects.select_related('user', 'room').filter(room__isnull=False).order_by('full_name')
        self.fields['scheduled_at'].required = False
        self.fields['scheduled_at'].help_text = 'Leave empty to send immediately'


# ─── USERNAME VALIDATION FORMS ────────────────────────

class UsernameUpdateForm(forms.ModelForm):
    """Form for updating username with robust validation."""
    
    class Meta:
        model = User
        fields = ['username']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter new username',
                'required': True
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = 'Username must be at least 3 characters long and unique.'
    
    def clean_username(self):
        """Validate username with case-insensitive uniqueness check."""
        username = self.cleaned_data.get('username')
        
        try:
            return UserService.validate_username(username, exclude_user_id=self.instance.id)
        except ValidationError as e:
            raise forms.ValidationError(str(e))


class UserRegistrationForm(forms.ModelForm):
    """Form for user registration with username validation."""
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Password must be at least 8 characters long.'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirm Password'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    def clean_username(self):
        """Validate username for new user registration."""
        username = self.cleaned_data.get('username')
        
        try:
            return UserService.validate_username(username)
        except ValidationError as e:
            raise forms.ValidationError(str(e))
    
    def clean_email(self):
        """Validate email uniqueness."""
        email = self.cleaned_data.get('email')
        
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Email is already registered.')
        
        return email
    
    def clean(self):
        """Validate password confirmation."""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')
        
        if password and len(password) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long.')
        
        return cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile with username validation."""
    
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 't-input'}),
        help_text='Username must be at least 3 characters long and unique.'
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 't-input'})
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 't-input',
            'type': 'tel',
            'pattern': '[0-9]{10,15}',
            'title': 'Phone number must contain only digits (10-15 numbers)',
            'placeholder': 'Enter phone number (10-15 digits)'
        }),
        help_text='Phone number must contain 10-15 digits only.'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 't-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and getattr(self.instance, 'username', None):
            self.fields['username'].initial = self.instance.username
        # Populate phone field from tenant profile if available
        if self.instance and hasattr(self.instance, 'tenantprofile'):
            self.fields['phone'].initial = self.instance.tenantprofile.phone or ''
    
    def clean_username(self):
        """Validate username with case-insensitive uniqueness check."""
        username = self.cleaned_data.get('username')
        
        try:
            return UserService.validate_username(username, exclude_user_id=self.instance.id)
        except ValidationError as e:
            raise forms.ValidationError(str(e))
    
    def clean_email(self):
        """Validate email uniqueness."""
        email = self.cleaned_data.get('email')
        
        if User.objects.filter(email__iexact=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('Email is already registered.')
        
        return email
    
    def clean_phone(self):
        """Validate phone number format and length."""
        import re
        phone = self.cleaned_data.get('phone', '').strip()
        
        if not phone:
            return ''
        
        # Remove non-digit characters for validation
        digits_only = re.sub(r'\D', '', phone)
        
        # Check length
        if len(digits_only) < 10:
            raise forms.ValidationError('Phone number must contain at least 10 digits.')
        if len(digits_only) > 15:
            raise forms.ValidationError('Phone number must contain at most 15 digits.')
        
        # Return digits only for storage
        return digits_only

