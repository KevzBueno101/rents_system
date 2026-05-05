"""
Authentication-related views: login, signup, logout, profile management.
"""
import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse, HttpResponseRedirect
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
        phone_raw = request.POST.get('phone')
        phone     = parse_phone(phone_raw)
        
        # Validate phone number
        if phone_raw and not phone:
            return render(request, 'login.html', {
                'signup_error'   : 'Phone number must contain 10-15 digits only.',
                'available_rooms': get_available_rooms(),
            })
        
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


class CustomPasswordResetForm(PasswordResetForm):
    """PasswordResetForm whose send_mail is actually invoked by form.save(); tracks delivery failures."""

    mail_delivery_failed = False

    def save(
        self,
        domain_override=None,
        subject_template_name='registration/password_reset_subject.txt',
        email_template_name='registration/password_reset_email.html',
        use_https=False,
        token_generator=default_token_generator,
        from_email=None,
        request=None,
        html_email_template_name=None,
        extra_email_context=None,
    ):
        self.mail_delivery_failed = False
        return super().save(
            domain_override=domain_override,
            subject_template_name=subject_template_name,
            email_template_name=email_template_name,
            use_https=use_https,
            token_generator=token_generator,
            from_email=from_email,
            request=request,
            html_email_template_name=html_email_template_name,
            extra_email_context=extra_email_context,
        )

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        """Send mail with SendGrid API, SMTP fallback, console fallback for DEBUG; marks mail_delivery_failed."""
        import logging

        from django.conf import settings
        from django.core.mail import send_mail as django_send_mail

        logger = logging.getLogger(__name__)

        # Try SendGrid HTTP API first when configured (not SMTP)
        try:
            sg_key = getattr(settings, 'SENDGRID_API_KEY', '') or ''
            if sg_key:
                import sendgrid
                from sendgrid.helpers.mail import Mail

                subject = render_to_string(subject_template_name, context)
                subject = ''.join(subject.splitlines())

                message = Mail(
                    from_email=from_email,
                    to_emails=to_email,
                    subject=subject,
                    html_content=(
                        render_to_string(html_email_template_name, context) if html_email_template_name else None
                    ),
                    plain_text_content=render_to_string(email_template_name, context),
                )

                sg = sendgrid.SendGridAPIClient(sg_key)
                response = sg.send(message)

                logger.info('SendGrid API email sent: %s to %s', response.status_code, to_email)
                return

        except Exception:
            logger.exception('SendGrid API failed for %s', to_email)

        try:
            return PasswordResetForm.send_mail(
                self,
                subject_template_name,
                email_template_name,
                context,
                from_email,
                to_email,
                html_email_template_name=html_email_template_name,
            )

        except Exception as smtp_error:
            logger.error('SMTP send failed for %s: %s', to_email, smtp_error, exc_info=True)

            try:
                from django.core.mail import get_connection

                connection = get_connection('django.core.mail.backends.console.EmailBackend')
                subject = render_to_string(subject_template_name, context)
                subject = ''.join(subject.splitlines())

                if html_email_template_name:
                    html_body = render_to_string(html_email_template_name, context)
                    email_message = EmailMultiAlternatives(subject, '', from_email, [to_email], connection=connection)
                    email_message.attach_alternative(html_body, 'text/html')
                    email_message.send()
                else:
                    plain_text = render_to_string(email_template_name, context)
                    django_send_mail(subject, plain_text, from_email, [to_email], connection=connection)

                logger.info('Console fallback email sent to %s', to_email)

            except Exception as console_error:
                logger.error('Console email fallback failed for %s: %s', to_email, console_error)
                logger.warning('All email methods failed for %s', to_email)
                self.mail_delivery_failed = True


class CustomPasswordResetView(PasswordResetView):
    """Password reset: SITE_URL in emails (domain_override), JSON for AJAX from login modal."""

    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.txt'
    html_email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = '/password-reset/done/'
    form_class = CustomPasswordResetForm

    @staticmethod
    def _expects_json(request):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return True
        accept = (request.headers.get('Accept') or '').lower()
        return 'application/json' in accept

    def form_invalid(self, form):
        if self._expects_json(self.request):
            return JsonResponse(
                {'ok': False, 'email_sent': False, 'errors': form.errors.as_json()},
                status=400,
            )
        return super().form_invalid(form)

    def form_valid(self, form):
        from django.conf import settings

        site_url = (getattr(settings, 'SITE_URL', '') or '').strip().rstrip('/')
        domain_only = (
            site_url.replace('http://', '', 1).replace('https://', '', 1)
            if site_url
            else ''
        )
        use_https = site_url.startswith('https://')

        extra = {'site_name': 'RENTS System'}
        if self.extra_email_context:
            extra.update(self.extra_email_context)

        opts = {
            'use_https': use_https,
            'domain_override': domain_only or None,
            'token_generator': self.token_generator,
            'from_email': self.from_email,
            'email_template_name': self.email_template_name,
            'subject_template_name': self.subject_template_name,
            'request': self.request,
            'html_email_template_name': self.html_email_template_name,
            'extra_email_context': extra,
        }

        try:
            form.save(**opts)
        except Exception as exc:
            if self._expects_json(self.request):
                return JsonResponse(
                    {'ok': False, 'email_sent': False, 'error': str(exc)},
                    status=503,
                )
            messages.error(
                self.request,
                'We could not send the password reset email. Try again later or contact support.',
            )
            return HttpResponseRedirect(self.get_success_url())

        failed = getattr(form, 'mail_delivery_failed', False)
        if failed:
            if self._expects_json(self.request):
                return JsonResponse(
                    {
                        'ok': False,
                        'email_sent': False,
                        'error': 'We could not send the password reset email. Try again later or contact support.',
                    },
                    status=503,
                )
            messages.error(
                self.request,
                'We could not send the password reset email. Try again later or contact support.',
            )
            return HttpResponseRedirect(self.get_success_url())

        if self._expects_json(self.request):
            return JsonResponse(
                {
                    'ok': True,
                    'email_sent': True,
                    'message': 'If an account with that email exists, a password reset link has been sent.',
                }
            )

        messages.info(
            self.request,
            'If an account with that email exists, a password reset link has been sent.',
        )
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.conf import settings

        su = (getattr(settings, 'SITE_URL', '') or '').strip().rstrip('/')
        context['domain'] = su.replace('http://', '').replace('https://', '')
        context['protocol'] = 'https' if su.startswith('https://') else 'http'
        return context

def custom_password_reset_confirm(request, uidb64, token):
    """
    Simple password reset confirm view that bypasses Django's authentication middleware.
    """
    from django.contrib.auth import get_user_model
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_decode
    from django.contrib.auth.forms import SetPasswordForm
    from django.shortcuts import render, redirect
    from django.contrib import messages
    
    User = get_user_model()
    
    # Try to decode the user ID
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    # Check if the token is valid
    validlink = user is not None and default_token_generator.check_token(user, token)
    
    if request.method == 'POST':
        if validlink:
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been reset successfully. You can now log in with your new password.')
                return redirect('password_reset_complete')
        else:
            # Invalid token - show error
            return render(request, 'registration/password_reset_confirm.html', {
                'validlink': False,
                'form': None
            })
    else:
        if validlink:
            form = SetPasswordForm(user)
        else:
            form = None
    
    return render(request, 'registration/password_reset_confirm.html', {
        'validlink': validlink,
        'form': form,
        'user': user
    })
