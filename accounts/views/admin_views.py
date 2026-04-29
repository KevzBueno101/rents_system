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


def audit_trail(request):
    """Display comprehensive audit trail with filtering and pagination (Admin only)."""
    if not request.user.is_staff:
        return redirect('tenant_dashboard')
    
    from django.core.paginator import Paginator
    from ..models import ActivityLog
    from django.contrib.auth.models import User
    from datetime import datetime
    
    # Get filter parameters
    user_filter = request.GET.get('user', '')
    action_filter = request.GET.get('action', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    content_type_filter = request.GET.get('content_type', '')
    search = request.GET.get('search', '')
    
    # Start with base queryset
    activities = ActivityLog.objects.all().select_related('user').order_by('-timestamp')
    
    # Apply filters safely
    if user_filter and user_filter.isdigit():
        activities = activities.filter(user_id=int(user_filter))
    
    if action_filter:
        activities = activities.filter(action=action_filter)
    
    if content_type_filter:
        activities = activities.filter(content_type__icontains=content_type_filter)
    
    if search:
        activities = activities.filter(description__icontains=search)
    
    # Date range filtering
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            activities = activities.filter(timestamp__date__gte=date_from_obj)
        except ValueError:
            pass  # Invalid date format, ignore filter
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            activities = activities.filter(timestamp__date__lte=date_to_obj)
        except ValueError:
            pass  # Invalid date format, ignore filter
    
    # Pagination (50 records per page)
    paginator = Paginator(activities, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options for dropdowns
    staff_users = User.objects.filter(is_staff=True).order_by('username')
    action_choices = ActivityLog.ACTION_CHOICES
    content_types = ActivityLog.objects.values_list('content_type', flat=True).distinct()
    content_types = [ct for ct in content_types if ct]  # Remove empty values
    
    # Preserve filters in pagination
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    
    context = {
        'page_obj': page_obj,
        'activities': page_obj,
        'staff_users': staff_users,
        'action_choices': action_choices,
        'content_types': content_types,
        'filters': {
            'user': user_filter,
            'action': action_filter,
            'date_from': date_from,
            'date_to': date_to,
            'content_type': content_type_filter,
            'search': search,
        },
        'query_params': query_params.urlencode(),
    }
    
    return render(request, 'admin/audit_trail.html', context)
