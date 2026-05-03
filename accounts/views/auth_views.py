"""
Authentication-related views: login, signup, logout, profile management.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.forms import PasswordResetForm
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError
from ..models import Room, TenantProfile, AdminProfile, Notification
from ..services.notification_service import NotificationService
from ..activity_utils import log_activity
from .helpers import parse_phone, get_available_rooms, get_dashboard_context
from accounts.services.user_service import UserService




def login_view(request):
    """Handle user login with role-based redirect."""
    # Always show login page - remove automatic redirect

    if request.method == 'POST':
        role     = request.POST.get('role')
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if role == 'admin' and user.is_staff:
                login(request, user)
                return redirect('admin_dashboard')
            elif role == 'tenant' and not user.is_staff:
                login(request, user)
                return redirect('tenant_dashboard')
            else:
                return render(request, 'login.html', {
                    'error_modal'    : True,
                    'error'          : 'Your account does not match the selected role.',
                    'available_rooms': get_available_rooms(),
                })
        else:
            return render(request, 'login.html', {
                'error_modal'    : True,
                'error'          : 'Invalid username or password.',
                'available_rooms': get_available_rooms(),
            })

    return render(request, 'login.html', {
        'available_rooms': get_available_rooms(),
    })


def signup_view(request):
    """Handle tenant self-signup with room selection."""
    if request.method == 'POST':
        username  = request.POST.get('username')
        password  = request.POST.get('password')
        email     = request.POST.get('email')
        full_name = request.POST.get('full_name')
        phone     = parse_phone(request.POST.get('phone'))
        room_id   = request.POST.get('room_id')
        photo     = request.FILES.get('photo')

        if not room_id:
            return render(request, 'login.html', {
                'signup_error'   : 'Please select a room.',
                'available_rooms': get_available_rooms(),
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'login.html', {
                'signup_error'   : 'Username already taken. Please choose another.',
                'available_rooms': get_available_rooms(),
            })

        if User.objects.filter(email__iexact=email).exists():
            return render(request, 'login.html', {
                'signup_error'   : 'This email is already registered. Please use a different email.',
                'available_rooms': get_available_rooms(),
            })

        try:
            selected_room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return render(request, 'login.html', {
                'signup_error'   : 'Selected room no longer available.',
                'available_rooms': get_available_rooms(),
            })

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )

        TenantProfile.objects.create(
            user=user,
            full_name=full_name,
            phone=phone,
            room=selected_room,
            room_number=selected_room.room_number,
            photo=photo
        )

        return render(request, 'login.html', {
            'signup_success' : 'Account created! You can now log in as Tenant.',
            'available_rooms': get_available_rooms(),
        })

    return redirect('login')


def logout_view(request):
    """Handle user logout."""
    logout(request)
    return redirect('login')


@login_required(login_url='/')
def edit_profile(request):
    """Role-aware profile page/update endpoint for admins and tenants."""
    if request.user.is_staff:
        return _edit_admin_profile(request)
    return _edit_tenant_profile(request)


def _edit_admin_profile(request):
    if request.method == 'POST':
        username         = request.POST.get('username')
        full_name        = request.POST.get('full_name')
        email            = request.POST.get('email')
        phone            = parse_phone(request.POST.get('phone'))
        current_password = request.POST.get('current_password')
        new_password     = request.POST.get('new_password') or request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        photo            = request.FILES.get('photo')

        errors = []

        if username and User.objects.filter(username=username).exclude(id=request.user.id).exists():
            errors.append('Username is already taken.')

        if email and User.objects.filter(email__iexact=email).exclude(id=request.user.id).exists():
            errors.append('Email is already registered.')

        if current_password and not request.user.check_password(current_password):
            errors.append('Current password is incorrect.')

        if new_password and new_password != confirm_password:
            errors.append('New passwords do not match.')

        if errors:
            return render(request, 'admin/dashboard.html', {
                **get_dashboard_context(),
                'profile_errors'    : errors,
                'show_profile_modal': True,
            })

        user          = request.user
        user.username = username or user.username
        user.email    = email or ''
        if new_password:
            user.set_password(new_password)
        user.save()
        if new_password:
            update_session_auth_hash(request, user)

        try:
            admin_profile = AdminProfile.objects.get(user=user)
        except AdminProfile.DoesNotExist:
            admin_profile = AdminProfile(user=user, created_by=user, full_name=full_name or user.username, phone=phone or '')

        admin_profile.full_name = full_name or user.username
        admin_profile.phone     = phone or ''
        if photo:
            admin_profile.photo = photo
        admin_profile.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('admin_dashboard')

    return redirect('admin_dashboard')


def _edit_tenant_profile(request):
    try:
        profile = TenantProfile.objects.select_related('user', 'room').get(user=request.user)
    except TenantProfile.DoesNotExist:
        messages.error(request, 'Tenant profile not found.')
        return redirect('tenant_dashboard')

    if request.method == 'POST':
        full_name        = request.POST.get('full_name', '').strip()
        new_username     = request.POST.get('username', '').strip()
        new_email        = request.POST.get('email', '').strip()
        phone_raw        = request.POST.get('phone', '').strip()
        current_password = request.POST.get('current_password')
        new_password     = request.POST.get('new_password') or request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        photo            = request.FILES.get('photo')

        errors = []

        if new_username and User.objects.filter(username=new_username).exclude(id=request.user.id).exists():
            errors.append('Username is already taken.')

        if new_email and User.objects.filter(email__iexact=new_email).exclude(id=request.user.id).exists():
            errors.append('Email is already registered.')

        if not full_name or len(full_name) < 2:
            errors.append('Full name must be at least 2 characters long.')

        phone = parse_phone(phone_raw) if phone_raw else None

        if new_password:
            if not current_password:
                errors.append('Current password is required to change your password.')
            elif not request.user.check_password(current_password):
                errors.append('Current password is incorrect.')
            elif len(new_password) < 8:
                errors.append('New password must be at least 8 characters long.')
            elif new_password != confirm_password:
                errors.append('New passwords do not match.')

        if errors:
            return render(request, 'tenant/tenant_profile.html', {
                'profile': profile,
                'profile_errors': errors,
            })

        user = request.user
        if new_username:
            user.username = new_username
        if new_email:
            user.email = new_email
        if new_password:
            user.set_password(new_password)
        user.save()
        if new_password:
            update_session_auth_hash(request, user)

        profile.full_name = full_name or profile.full_name
        if phone_raw:
            profile.phone = phone
        if photo:
            profile.photo = photo
        profile.save()

        log_activity(
            user=request.user,
            action='tenant_updated',
            description='Updated profile information',
            content_type='TenantProfile',
            object_id=profile.id
        )

        messages.success(request, 'Profile updated successfully.')
        return redirect('edit_profile')

    completion_fields = {
        'full_name': bool(profile.full_name),
        'email': bool(profile.user.email),
        'phone': bool(profile.phone),
        'photo': bool(profile.photo),
        'room': bool(profile.room)
    }
    completion_percentage = (sum(completion_fields.values()) / len(completion_fields)) * 100

    return render(request, 'tenant/tenant_profile.html', {
        'profile': profile,
        'completion_percentage': completion_percentage,
        'completion_fields': completion_fields,
        'filled_fields_count': sum(completion_fields.values()),
    })
class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view with security improvements."""
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.txt'
    html_email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = '/password-reset/done/'
    form_class = PasswordResetForm
    
    def form_valid(self, form):
        # Check if user exists before sending email
        email = form.cleaned_data['email']
        users = User.objects.filter(email=email)
        
        if not users.exists():
            # Don't reveal if email exists or not for security
            messages.info(self.request, 'If an account with that email exists, a password reset link has been sent.')
            return super().form_valid(form)
        
        return super().form_valid(form)
    
    def send_mail(self, subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name=None):
        """
        Override send_mail to properly handle HTML emails with plain text fallback
        """
        subject = render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())
        
        # Render HTML email
        html_email = render_to_string(email_template_name, context)
        
        # Create plain text version from HTML for email clients that don't support HTML
        import re
        plain_text = re.sub(r'<[^>]+>', '', html_email)
        plain_text = re.sub(r'\s+', ' ', plain_text).strip()
        
        # Create email with plain text content and HTML alternative
        email_message = EmailMultiAlternatives(subject, plain_text, from_email, [to_email])
        email_message.attach_alternative(html_email, "text/html")
        email_message.send()


@login_required
def mark_notification(request, notif_id):
    """
    Enhanced notification handler with security and logging.
    
    Security: Ensures users can only access their own notifications
    Performance: Uses NotificationService for optimized operations
    Logging: Tracks notification interactions for audit trail
    """
    try:
        # Use NotificationService for secure notification access
        success = NotificationService.mark_as_read(
            notification_id=notif_id,
            user=request.user
        )
        
        if not success:
            messages.error(request, 'Notification not found or access denied.')
            return redirect('admin_dashboard' if request.user.is_staff else 'tenant_dashboard')
        
        # Get the notification for redirect (already verified as belonging to user)
        notification = Notification.objects.get(id=notif_id, user=request.user)
        
        # Log the notification interaction for audit trail
        log_activity(
            user=request.user,
            action='notification_read',
            description=f'Read notification: {notification.title}',
            content_type='Notification',
            object_id=notification.id
        )
        
        # Dynamic redirect based on notification link or fallback
        redirect_url = notification.get_absolute_url()
        return redirect(redirect_url)
                
    except Exception as e:
        # Log unexpected errors but don't expose them to user
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error processing notification {notif_id}: {e}")
        
        messages.error(request, 'An error occurred while processing the notification.')
        return redirect('admin_dashboard' if request.user.is_staff else 'tenant_dashboard')

@login_required
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Custom password reset confirm view."""
    template_name = 'registration/password_reset_confirm.html'
    success_url = '/password-reset/complete/'
    
    def form_valid(self, form):
        messages.success(self.request, 'Your password has been reset successfully. You can now log in with your new password.')
        return super().form_valid(form)
