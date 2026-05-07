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
        from tenant.services.dashboard_service import get_tenant_dashboard_data
        from maintenance.services.maintenance_service import get_upcoming_payment

        data = get_tenant_dashboard_data(request.user)
        data['profile'] = data.get('tenant')
        data['payment'] = get_upcoming_payment(request.user)
        
        # Get admin phone number for contact display
        try:
            from ..models import AdminProfile
            admin_profile = AdminProfile.objects.filter(user__is_superuser=True).first()
            data['admin_phone'] = admin_profile.phone if admin_profile else 'Contact Admin'
        except Exception:
            data['admin_phone'] = 'Contact Admin'

        return render(request, 'tenant/tenant_dashboard.html', data)
    except TenantProfile.DoesNotExist:
        messages.error(request, 'Tenant profile not found.')
        return redirect('login')


@login_required(login_url='/')
def tenant_bills(request):
    """Tenant-only billing history."""
    if request.user.is_staff:
        return redirect('admin_dashboard')

    from tenant.services.dashboard_service import get_tenant_dashboard_data
    dashboard_data = get_tenant_dashboard_data(request.user)
    
    # Get admin phone number for contact display
    try:
        from ..models import AdminProfile
        admin_profile = AdminProfile.objects.filter(user__is_superuser=True).first()
        admin_phone = admin_profile.phone if admin_profile else 'Contact Admin'
    except Exception:
        admin_phone = 'Contact Admin'

    status_filter = request.GET.get('status', '')
    bills = (
        Bill.objects.filter(tenant=dashboard_data['tenant'])
        .select_related('tenant', 'room')
        .prefetch_related('payments', 'items')
        .order_by('-created_at')
    )
    if status_filter:
        bills = bills.filter(status=status_filter)

    all_bills = Bill.objects.filter(tenant=dashboard_data['tenant'])
    total_billed = all_bills.aggregate(total=Sum('total_amount'))['total'] or 0
    total_paid = all_bills.aggregate(total=Sum('payments__amount'))['total'] or 0

    from datetime import datetime
    current_month = datetime.now().month
    current_year = datetime.now().year

    this_month_bills = all_bills.filter(
        created_at__month=current_month,
        created_at__year=current_year
    )
    this_month_billed = this_month_bills.aggregate(total=Sum('total_amount'))['total'] or 0

    bill_count = all_bills.count()
    average_bill = total_billed / bill_count if bill_count > 0 else 0

    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    is_mobile = any(mobile in user_agent for mobile in ['mobile', 'android', 'iphone', 'ipad', 'tablet'])

    template_name = 'tenant/tenant_bills_mobile.html' if is_mobile else 'tenant/tenant_bills.html'

    context = {
        **dashboard_data,
        'bills': bills,
        'status_filter': status_filter,
        'total_billed': total_billed,
        'total_paid': total_paid,
        'total_outstanding': total_billed - total_paid,
        'paid_bills': all_bills.filter(status='paid').count(),
        'overdue_count': all_bills.filter(status='overdue').count(),
        'admin_phone': admin_phone,
        'this_month_billed': this_month_billed,
        'average_bill': average_bill,
        'is_mobile': is_mobile,
    }

    return render(request, template_name, context)


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
        username  = request.POST.get('username', '').strip()
        password  = request.POST.get('password', '').strip()
        email     = request.POST.get('email', '').strip()
        full_name = request.POST.get('full_name', '').strip()
        phone_raw = request.POST.get('phone', '').strip()
        phone     = parse_phone(phone_raw)
        room_id   = request.POST.get('room_id', '').strip()
        photo     = request.FILES.get('photo')

        def render_error(error_msg):
            return render(request, 'admin/tenant_list.html', {
                'tenants'        : TenantProfile.objects.select_related('user', 'room').order_by('-created_at'),
                'add_error'      : error_msg,
                'show_add_modal' : True,
                'available_rooms': get_available_rooms(),
            })

        # ── VALIDATE ALL FIELDS BEFORE TOUCHING THE DB ──
        if not full_name:
            return render_error('Full name is required.')
        if not email:
            return render_error('Email is required.')
        if not phone_raw:
            return render_error('Phone number is required.')
        if phone is None:
            return render_error('Phone number must contain 10–15 digits only.')
        if not username:
            return render_error('Username is required.')
        if len(username) < 3:
            return render_error('Username must be at least 3 characters long.')
        if not password:
            return render_error('Password is required.')
        if len(password) < 8:
            return render_error('Password must be at least 8 characters long.')
        if not room_id:
            return render_error('Please select a room.')
        if User.objects.filter(username__iexact=username).exists():
            return render_error('Username already taken.')
        if User.objects.filter(email__iexact=email).exists():
            return render_error('This email is already registered. Please use a different email.')

        try:
            selected_room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return render_error('Selected room no longer exists.')

        # ── ALL VALID — CREATE USER & PROFILE ──
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            is_staff=False,
        )

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
        full_name = request.POST.get('full_name', '').strip()
        new_email = request.POST.get('email', '').strip()
        phone_raw = request.POST.get('phone', '').strip()
        phone     = parse_phone(phone_raw)
        room_id   = request.POST.get('room_id', '').strip()

        def render_error(error_msg):
            return render(request, 'admin/tenant_list.html', {
                'tenants'        : TenantProfile.objects.select_related('user', 'room').order_by('-created_at'),
                'edit_error'     : error_msg,
                'show_edit_modal': True,
                'available_rooms': get_available_rooms(),
            })

        # ── VALIDATE ALL FIELDS ──
        if not full_name:
            return render_error('Full name is required.')
        if not new_email:
            return render_error('Email is required.')
        if not phone_raw:
            return render_error('Phone number is required.')
        if phone is None:
            return render_error('Phone number must contain 10–15 digits only.')
        if not room_id:
            return render_error('Please select a room.')
        if User.objects.filter(email__iexact=new_email).exclude(id=tenant.user.id).exists():
            return render_error('This email is already registered. Please use a different email.')

        try:
            selected_room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return render_error('Selected room no longer exists.')

        # ── ALL VALID — UPDATE ──
        tenant.full_name  = full_name
        tenant.phone      = phone
        tenant.user.email = new_email
        tenant.room       = selected_room
        tenant.room_number = selected_room.room_number

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