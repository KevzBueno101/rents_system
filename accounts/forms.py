from django import forms
from django.forms import formset_factory
from .models import Bill, BillItem, Payment, TenantProfile, TenantReminder
from django.utils import timezone


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
