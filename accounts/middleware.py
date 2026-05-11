"""
Security middleware: admin portal brute-force protection, RBAC portal isolation,
and baseline security headers.
"""
import logging
from urllib.parse import quote

from django.conf import settings
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect
from django.urls import Resolver404, resolve, reverse

# Import messages safely to avoid circular import issues
try:
    from django.contrib import messages
    MESSAGES_AVAILABLE = True
except ImportError:
    MESSAGES_AVAILABLE = False

from accounts.rbac.admin_login_throttle import (
    get_client_ip,
    is_admin_login_locked,
)
from accounts.rbac.policy import (
    PUBLIC_ROUTE_NAMES,
    SHARED_AUTH_ROUTE_NAMES,
    STAFF_PORTAL_ROUTE_NAMES,
    TENANT_PORTAL_ROUTE_NAMES,
)

logger = logging.getLogger(__name__)


DJANGO_ADMIN_PATH_PREFIXES = getattr(
    settings,
    'DJANGO_SITE_ADMIN_PATH_PREFIXES',
    ('/django-admin',),
)


class PortalRBACMiddleware:
    """
    Enforces tenant-vs-staff access by named route and drives correct login redirects.
    Complements Django session auth by blocking cross-privilege navigation and API churn.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path_info = request.path_info

        for prefix in DJANGO_ADMIN_PATH_PREFIXES:
            if path_info.startswith(prefix):
                return self.get_response(request)

        static_prefix = getattr(settings, 'STATIC_URL', '/static/')
        if static_prefix and not static_prefix.startswith('/'):
            static_prefix = '/' + static_prefix.lstrip('/')
        static_prefix = static_prefix.rstrip('/')
        if static_prefix and (path_info == static_prefix or path_info.startswith(static_prefix + '/')):
            return self.get_response(request)

        media_url = (getattr(settings, 'MEDIA_URL', '') or '').strip().rstrip('/')
        if media_url:
            if not media_url.startswith('/'):
                media_url = '/' + media_url.lstrip('/')
            if path_info == media_url or path_info.startswith(media_url + '/'):
                return self.get_response(request)

        if not path_info.startswith('/'):
            return self.get_response(request)

        try:
            match = resolve(path_info)
        except Resolver404:
            return self.get_response(request)

        url_name = match.url_name

        if url_name in PUBLIC_ROUTE_NAMES:
            return self.get_response(request)

        if not request.user.is_authenticated:
            if url_name in STAFF_PORTAL_ROUTE_NAMES:
                next_q = quote(request.get_full_path(), safe='/')
                return redirect(f'{reverse("admin_login")}?next={next_q}')
            if url_name in TENANT_PORTAL_ROUTE_NAMES:
                next_q = quote(request.get_full_path(), safe='/')
                return redirect(f'{reverse("login")}?next={next_q}')
            return self.get_response(request)

        if url_name in SHARED_AUTH_ROUTE_NAMES or url_name in PUBLIC_ROUTE_NAMES:
            return self.get_response(request)

        if url_name in TENANT_PORTAL_ROUTE_NAMES:
            if request.user.is_staff:
                if path_info.startswith('/api/'):
                    return JsonResponse({'success': False, 'error': 'Forbidden'}, status=403)
                if MESSAGES_AVAILABLE:
                    messages.warning(request, 'Staff accounts cannot use tenant screens.')
                return redirect('admin_dashboard')
            return self.get_response(request)

        if url_name in STAFF_PORTAL_ROUTE_NAMES:
            if not request.user.is_staff:
                if path_info.startswith('/api/'):
                    return JsonResponse({'success': False, 'error': 'Forbidden'}, status=403)
                try:
                    messages.error(request, 'Sign in via the administrator portal.')
                except Exception:
                    pass  # MessageMiddleware not active; redirect will still proceed
                next_q = quote(request.get_full_path(), safe='/')
                return redirect(f'{reverse("admin_login")}?next={next_q}')
            return self.get_response(request)

        return self.get_response(request)


class AdminLoginProtectionMiddleware:
    """
    IP lockout gate for /admin/login/ (attempt accounting is driven by the login view).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        canonical = reverse('admin_login').rstrip('/')
        if request.path_info.rstrip('/') == canonical:
            ip_address = get_client_ip(request)
            if is_admin_login_locked(ip_address):
                logger.warning('Blocked admin portal login attempt from locked IP: %s', ip_address)
                return HttpResponseForbidden('Too many failed attempts. Please try again later.')

        return self.get_response(request)


class SecurityHeadersMiddleware:
    """Add conservative security headers to HTML responses."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.setdefault('X-Content-Type-Options', 'nosniff')
        response.setdefault('X-Frame-Options', 'DENY')
        response.setdefault('X-XSS-Protection', '1; mode=block')
        response.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        if hasattr(response, 'headers'):
            if 'Server' in response.headers:
                del response.headers['Server']
        return response
