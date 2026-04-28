"""
Admin management views: dashboard, list, register, toggle status, delete.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from ..models import AdminProfile
from ..activity_utils import log_activity
from .helpers import parse_phone, get_dashboard_context


def admin_dashboard(request):
    """Admin dashboard with stats and recent activities."""
    if not request.user.is_staff:
        return redirect('tenant_dashboard')
    context = get_dashboard_context()
    from ..activity_utils import get_recent_activities
    context['activities'] = get_recent_activities(limit=3)
    return render(request, 'admin/dashboard.html', context)


def admin_list(request):
    """List all admins with search functionality (Superadmin only)."""
    if not request.user.is_superuser:
        return redirect('admin_dashboard')

    search = request.GET.get('search', '')
    admins = AdminProfile.objects.select_related('user', 'created_by').order_by('-created_at')

    if search:
        admins = admins.filter(
            Q(full_name__icontains=search) |
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search) |
            Q(phone__icontains=search)
        )

    return render(request, 'admin/admin_list.html', {'admins': admins, 'search': search})


def register_admin(request):
    """Register a new admin account (Superadmin only)."""
    if not request.user.is_superuser:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        username  = request.POST.get('username')
        password  = request.POST.get('password')
        email     = request.POST.get('email')
        full_name = request.POST.get('full_name')
        phone     = parse_phone(request.POST.get('phone'))
        photo     = request.FILES.get('photo')

        if User.objects.filter(username=username).exists():
            return render(request, 'admin/admin_list.html', {
                'admins'              : AdminProfile.objects.select_related('user', 'created_by').order_by('-created_at'),
                'register_error'      : 'Username already taken.',
                'show_register_modal': True,
            })

        if User.objects.filter(email__iexact=email).exists():
            return render(request, 'admin/admin_list.html', {
                'admins'              : AdminProfile.objects.select_related('user', 'created_by').order_by('-created_at'),
                'register_error'      : 'This email is already registered. Please use a different email.',
                'show_register_modal': True,
            })

        new_admin = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            is_staff=True,
            is_superuser=False,
        )

        admin_profile = AdminProfile.objects.create(
            user=new_admin,
            full_name=full_name,
            phone=phone,
            photo=photo,
            created_by=request.user
        )

        log_activity(
            user=request.user,
            action='admin_created',
            description=f'Registered admin {full_name}',
            content_type='AdminProfile',
            object_id=admin_profile.id
        )

        return render(request, 'admin/dashboard.html', {
            **get_dashboard_context(),
            'register_success': f'Admin account for {full_name} created successfully!',
        })

    return redirect('admin_dashboard')


def toggle_admin_status(request, user_id):
    """Toggle admin active/inactive status (Superadmin only)."""
    if not request.user.is_superuser:
        return redirect('admin_dashboard')

    admin_user = User.objects.get(id=user_id)
    admin_user.is_active = not admin_user.is_active
    status = 'activated' if admin_user.is_active else 'deactivated'
    
    log_activity(
        user=request.user,
        action='admin_updated',
        description=f'{status} admin {admin_user.username}',
        content_type='AdminProfile',
        object_id=admin_user.adminprofile.id
    )
    
    admin_user.save()
    return redirect('admin_list')


def delete_admin(request, user_id):
    """Delete an admin account (Superadmin only)."""
    if not request.user.is_superuser:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        admin_user = User.objects.get(id=user_id)
        admin_name = admin_user.adminprofile.full_name
        admin_id_log = admin_user.adminprofile.id
        
        log_activity(
            user=request.user,
            action='admin_deleted',
            description=f'Deleted admin {admin_name}',
            content_type='AdminProfile',
            object_id=admin_id_log
        )
        
        admin_user.delete()

    return redirect('admin_list')
