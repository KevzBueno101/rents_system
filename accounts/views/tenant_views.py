"""
Tenant management views: dashboard, list, add, edit, delete.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Sum
from ..models import Bill, MaintenanceReport, Room, TenantProfile, Violation
from ..activity_utils import log_activity
from .helpers import parse_phone, get_available_rooms


@login_required(login_url='/')
def tenant_dashboard(request):
    """Tenant-only dashboard."""
    if request.user.is_staff:
        return redirect('admin_dashboard')
    
    try:
        profile = TenantProfile.objects.select_related('user', 'room').get(user=request.user)
    except TenantProfile.DoesNotExist:
        messages.error(request, 'Tenant profile not found.')
        return redirect('login')
    
    return render(request, 'tenant/dashboard.html', {'profile': profile})

@login_required(login_url='/')
def tenant_bills(request):
    """Tenant-only billing history."""
    if request.user.is_staff:
        return redirect('admin_dashboard')

    profile = TenantProfile.objects.select_related('user', 'room').get(user=request.user)
    status_filter = request.GET.get('status', '')
    bills = (
        Bill.objects.filter(tenant=profile)
        .select_related('tenant', 'room')
        .prefetch_related('payments', 'items')
        .order_by('-created_at')
    )
    if status_filter:
        bills = bills.filter(status=status_filter)

    all_bills = Bill.objects.filter(tenant=profile)
    total_billed = all_bills.aggregate(total=Sum('total_amount'))['total'] or 0
    total_paid = sum(bill.paid_amount for bill in all_bills)

    # Calculate additional stats
    from datetime import datetime
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    this_month_bills = all_bills.filter(
        created_at__month=current_month,
        created_at__year=current_year
    )
    this_month_billed = this_month_bills.aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Calculate average bill amount
    bill_count = all_bills.count()
    average_bill = total_billed / bill_count if bill_count > 0 else 0

    # Detect mobile device
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    is_mobile = any(mobile in user_agent for mobile in ['mobile', 'android', 'iphone', 'ipad', 'tablet'])
    
    # Choose template based on device
    template_name = 'tenant/tenant_bills_mobile.html' if is_mobile else 'tenant/tenant_bills.html'
    
    return render(request, template_name, {
        'profile': profile,
        'bills': bills,
        'status_filter': status_filter,
        'total_billed': total_billed,
        'total_paid': total_paid,
        'total_outstanding': total_billed - total_paid,
        'paid_bills': all_bills.filter(status='paid').count(),
        'overdue_count': all_bills.filter(status='overdue').count(),
        'this_month_billed': this_month_billed,
        'average_bill': average_bill,
        'is_mobile': is_mobile,
    })


@login_required(login_url='/')
def tenant_reports(request):
    """Tenant-only maintenance and violation history."""
    if request.user.is_staff:
        return redirect('admin_dashboard')

    profile = TenantProfile.objects.select_related('user', 'room').get(user=request.user)
    maintenance_reports = MaintenanceReport.objects.filter(tenant=profile).order_by('-created_at')
    violations = Violation.objects.filter(tenant=profile).order_by('-date')

    return render(request, 'tenant/tenant_reports.html', {
        'profile': profile,
        'maintenance_reports': maintenance_reports,
        'maintenance_open_count': maintenance_reports.filter(status__in=['open', 'ongoing']).count(),
        'violations': violations,
        'active_tab': request.GET.get('tab', 'maintenance'),
    })


@login_required(login_url='/')
def tenant_submit_maintenance(request):
    """Allow tenants to submit their own maintenance requests."""
    if request.user.is_staff:
        return redirect('admin_dashboard')

    profile = TenantProfile.objects.get(user=request.user)
    if request.method == 'POST':
        description = request.POST.get('description', '').strip()
        if description:
            report = MaintenanceReport.objects.create(tenant=profile, description=description)
            log_activity(
                user=request.user,
                action='maintenance_created',
                description=f'Tenant submitted maintenance request for {profile.full_name}',
                content_type='MaintenanceReport',
                object_id=report.id
            )
            messages.success(request, 'Maintenance request submitted.')
        else:
            messages.error(request, 'Please describe the maintenance issue.')

    return redirect('tenant_reports')


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
