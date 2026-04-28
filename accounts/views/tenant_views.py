"""
Tenant management views: dashboard, list, add, edit, delete.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from ..models import Room, TenantProfile
from ..activity_utils import log_activity
from .helpers import parse_phone, get_available_rooms


@login_required(login_url='/')
def tenant_dashboard(request):
    """Tenant dashboard showing personal info."""
    if request.user.is_staff:
        return redirect('admin_dashboard')
    profile = TenantProfile.objects.get(user=request.user)
    return render(request, 'tenant/dashboard.html', {'profile': profile})


def tenant_list(request):
    """List all tenants with search functionality."""
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    search  = request.GET.get('search', '')
    tenants = TenantProfile.objects.select_related('user', 'room').order_by('-created_at')

    if search:
        tenants = tenants.filter(
            Q(full_name__icontains=search) |
            Q(phone__icontains=search) |
            Q(room_number__icontains=search) |
            Q(user__email__icontains=search) |
            Q(user__username__icontains=search)
        )

    return render(request, 'admin/tenant_list.html', {
        'tenants'        : tenants,
        'search'         : search,
        'available_rooms': get_available_rooms(),
    })


def add_tenant(request):
    """Add a new tenant."""
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    if request.method == 'POST':
        username  = request.POST.get('username')
        password  = request.POST.get('password')
        email     = request.POST.get('email')
        full_name = request.POST.get('full_name')
        phone     = parse_phone(request.POST.get('phone'))
        room_id   = request.POST.get('room_id')
        photo     = request.FILES.get('photo')

        if User.objects.filter(username=username).exists():
            return render(request, 'admin/tenant_list.html', {
                'tenants'        : TenantProfile.objects.select_related('user', 'room').order_by('-created_at'),
                'add_error'      : 'Username already taken.',
                'show_add_modal' : True,
                'available_rooms': get_available_rooms(),
            })

        if User.objects.filter(email__iexact=email).exists():
            return render(request, 'admin/tenant_list.html', {
                'tenants'        : TenantProfile.objects.select_related('user', 'room').order_by('-created_at'),
                'add_error'      : 'This email is already registered. Please use a different email.',
                'show_add_modal' : True,
                'available_rooms': get_available_rooms(),
            })

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            is_staff=False,
        )

        selected_room = Room.objects.get(id=room_id)

        tenant = TenantProfile.objects.create(
            user=user,
            full_name=full_name,
            phone=phone,
            room=selected_room,
            room_number=selected_room.room_number,
            photo=photo,
        )

        log_activity(
            user=request.user,
            action='tenant_created',
            description=f'Added tenant {full_name} to {selected_room.room_number}',
            content_type='TenantProfile',
            object_id=tenant.id
        )

        return redirect('tenant_list')

    return redirect('tenant_list')


def edit_tenant(request, tenant_id):
    """Edit tenant information."""
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    tenant = TenantProfile.objects.get(id=tenant_id)

    if request.method == 'POST':
        new_email = request.POST.get('email')
        
        # Check if email is already used by another user (excluding current user)
        if User.objects.filter(email__iexact=new_email).exclude(id=tenant.user.id).exists():
            return render(request, 'admin/tenant_list.html', {
                'tenants'        : TenantProfile.objects.select_related('user', 'room').order_by('-created_at'),
                'edit_error'     : 'This email is already registered. Please use a different email.',
                'show_edit_modal': True,
                'available_rooms': get_available_rooms(),
            })
        
        tenant.full_name  = request.POST.get('full_name')
        tenant.phone      = parse_phone(request.POST.get('phone'))
        tenant.user.email = new_email

        # Fixed: update room FK properly using room_id
        room_id = request.POST.get('room_id')
        if room_id:
            try:
                selected_room = Room.objects.get(id=room_id)
                tenant.room = selected_room
                tenant.room_number = selected_room.room_number
            except Room.DoesNotExist:
                pass

        if request.FILES.get('photo'):
            tenant.photo = request.FILES.get('photo')

        tenant.save()
        tenant.user.save()

        log_activity(
            user=request.user,
            action='tenant_updated',
            description=f'Updated tenant {tenant.full_name}',
            content_type='TenantProfile',
            object_id=tenant.id
        )

        return redirect('tenant_list')

    return redirect('tenant_list')


def delete_tenant(request, tenant_id):
    """Delete a tenant."""
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    if request.method == 'POST':
        tenant = TenantProfile.objects.get(id=tenant_id)
        tenant_name = tenant.full_name
        tenant_id_log = tenant.id
        
        log_activity(
            user=request.user,
            action='tenant_deleted',
            description=f'Deleted tenant {tenant_name}',
            content_type='TenantProfile',
            object_id=tenant_id_log
        )
        
        tenant.user.delete()

    return redirect('tenant_list')
