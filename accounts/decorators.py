"""
Security decorators for role-based access control and route protection.
"""
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def admin_required(view_func):
    """
    Authenticated Django staff-only views (management portal session).
    """
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, 'Admin access denied.')
            return redirect('tenant_dashboard')
        return view_func(request, *args, **kwargs)

    return login_required(_wrapped_view, login_url='/admin/login/')


def tenant_required(view_func):
    """
    Authenticated non-staff tenants only.
    """
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_staff:
            messages.warning(request, 'Admin accounts use the administrator dashboard.')
            return redirect('admin_dashboard')
        return view_func(request, *args, **kwargs)

    return login_required(_wrapped_view, login_url='/login/')


def superadmin_required(view_func):
    """Django superuser only (elevated administrative actions)."""
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, 'Superadmin access denied.')
            return redirect('admin_dashboard')
        return view_func(request, *args, **kwargs)

    return login_required(_wrapped_view, login_url='/admin/login/')


def prevent_staff_tenant_access(view_func):
    """
    Block staff from tenant-facing view functions (typically paired with tenant login).
    """
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            messages.error(request, 'This area is for tenants only.')
            return redirect('admin_dashboard')

        return view_func(request, *args, **kwargs)

    return login_required(_wrapped_view, login_url='/login/')
