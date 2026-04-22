from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import TenantProfile, Room, Bill, MaintenanceReport, Violation, AdminProfile


# ─── LOGIN ───────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        else:
            return redirect('tenant_dashboard')

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
                    'error_modal': True,
                    'error': 'Your account does not match the selected role.'
                })
        else:
            return render(request, 'login.html', {
                'error_modal': True,
                'error': 'Invalid username or password.'
            })

    # Get available rooms for signup dropdown
    from django.db.models import Count, Q
    available_rooms = Room.objects.annotate(
        occupied_count=Count('tenantprofile', filter=Q(tenantprofile__isnull=False))
    ).filter(
        capacity__gt=models.F('occupied_count')
    ).order_by('floor', 'room_number')
    
    return render(request, 'login.html', {
        'available_rooms': available_rooms
    })


# ─── SIGNUP ──────────────────────────────────────────
def signup_view(request):
    # Get available rooms (not full)
    from django.db.models import Count, Q
    
    available_rooms = Room.objects.annotate(
        occupied_count=Count('tenantprofile', filter=Q(tenantprofile__isnull=False))
    ).filter(
        capacity__gt=models.F('occupied_count')
    ).order_by('floor', 'room_number')
    
    if request.method == 'POST':
        username    = request.POST.get('username')
        password    = request.POST.get('password')
        email       = request.POST.get('email')
        full_name   = request.POST.get('full_name')
        phone       = request.POST.get('phone')
        room_id     = request.POST.get('room_id')
        photo       = request.FILES.get('photo')

        # Validate all required fields
        errors = []
        
        if not username:
            errors.append('Username is required.')
        elif User.objects.filter(username=username).exists():
            errors.append('Username already taken. Please choose another.')
            
        if not password:
            errors.append('Password is required.')
            
        if not email:
            errors.append('Email is required.')
            
        if not full_name:
            errors.append('Full name is required.')
            
        if not phone:
            errors.append('Phone number is required.')
            
        if not room_id:
            errors.append('Please select a room.')
        else:
            try:
                selected_room = Room.objects.get(id=room_id)
            except Room.DoesNotExist:
                errors.append('Selected room is no longer available.')

        # If there are errors, return with error messages
        if errors:
            return render(request, 'login.html', {
                'signup_error': errors[0],  # Show first error
                'available_rooms': available_rooms  # Re-populate room dropdown
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
            room_id=room_id,
            room=selected_room,
            room_number=selected_room.room_number,  # Keep for backward compatibility
            photo=photo
        )

        return render(request, 'login.html', {
            'signup_success': 'Account created! You can now log in as Tenant.'
        })

    return redirect('login')


# ─── REGISTER ADMIN (Superadmin only) ────────────────
@login_required(login_url='/')
def register_admin(request):
    if not request.user.is_superuser:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        username  = request.POST.get('username')
        password  = request.POST.get('password')
        email     = request.POST.get('email')
        full_name = request.POST.get('full_name')
        phone     = request.POST.get('phone')
        photo     = request.FILES.get('photo')

        if User.objects.filter(username=username).exists():
            return render(request, 'admin/dashboard.html', {
                'register_error'     : 'Username already taken.',
                'show_register_modal': True,
                'total_tenants'      : TenantProfile.objects.count(),
                'vacant_rooms'       : sum(1 for r in Room.objects.all() if not r.is_full()),
                'unpaid_bills'       : Bill.objects.filter(is_paid=False).count(),
                'open_repairs'       : MaintenanceReport.objects.filter(status='open').count(),
                'recent_tenants'     : TenantProfile.objects.order_by('-created_at')[:5],
            })

        new_admin = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            is_staff=True,
            is_superuser=False,
        )

        AdminProfile.objects.create(
            user=new_admin,
            full_name=full_name,
            phone=phone,
            photo=photo,
            created_by=request.user
        )

        return render(request, 'admin/dashboard.html', {
            'register_success': f'Admin account for {full_name} created successfully!',
            'total_tenants'   : TenantProfile.objects.count(),
            'vacant_rooms'    : sum(1 for r in Room.objects.all() if not r.is_full()),
            'unpaid_bills'    : Bill.objects.filter(is_paid=False).count(),
            'open_repairs'    : MaintenanceReport.objects.filter(status='open').count(),
            'recent_tenants'  : TenantProfile.objects.order_by('-created_at')[:5],
        })

    return redirect('admin_dashboard')


# ─── ADMIN DASHBOARD ─────────────────────────────────
@login_required(login_url='/')
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    all_rooms      = Room.objects.all()
    total_tenants  = TenantProfile.objects.count()
    vacant_rooms   = sum(1 for r in all_rooms if not r.is_full())
    unpaid_bills   = Bill.objects.filter(is_paid=False).count()
    open_repairs   = MaintenanceReport.objects.filter(status='open').count()
    recent_tenants = TenantProfile.objects.order_by('-created_at')[:5]
    total_beds     = sum(r.capacity for r in all_rooms)
    occupied_beds  = sum(r.occupied_beds() for r in all_rooms)
    vacant_beds    = total_beds - occupied_beds
    occupancy_rate = (occupied_beds / total_beds * 100) if total_beds > 0 else 0

    occupied_rooms = [r for r in all_rooms if r.occupied_beds() > 0]
    if len(occupied_rooms) < 3:
        vacant = [r for r in all_rooms if r.occupied_beds() == 0]
        occupied_rooms = occupied_rooms + vacant[:3 - len(occupied_rooms)]

    return render(request, 'admin/dashboard.html', {
        'total_tenants' : total_tenants,
        'vacant_rooms'  : vacant_rooms,
        'unpaid_bills'  : unpaid_bills,
        'open_repairs'  : open_repairs,
        'recent_tenants': recent_tenants,
        'total_beds'    : total_beds,
        'vacant_beds'   : vacant_beds,
        'occupied_beds' : occupied_beds,
        'occupancy_rate': occupancy_rate,
        'recent_rooms'  : occupied_rooms[:3],
    })


# ─── ADMIN LIST (Superadmin only) ────────────────────
@login_required(login_url='/')
def admin_list(request):
    if not request.user.is_superuser:
        return redirect('admin_dashboard')

    admins = AdminProfile.objects.select_related('user', 'created_by').order_by('-created_at')

    return render(request, 'admin/admin_list.html', {
        'admins': admins,
    })


# ─── TOGGLE ADMIN STATUS (Superadmin only) ────────────
@login_required(login_url='/')
def toggle_admin_status(request, user_id):
    if not request.user.is_superuser:
        return redirect('admin_dashboard')

    admin_user = User.objects.get(id=user_id)
    admin_user.is_active = not admin_user.is_active
    admin_user.save()

    return redirect('admin_list')


# ─── DELETE ADMIN (Superadmin only) ──────────────────
@login_required(login_url='/')
def delete_admin(request, user_id):
    if not request.user.is_superuser:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        admin_user = User.objects.get(id=user_id)
        admin_user.delete()

    return redirect('admin_list')


# ─── TENANT DASHBOARD ────────────────────────────────
@login_required(login_url='/')
def tenant_dashboard(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    profile = TenantProfile.objects.get(user=request.user)
    return render(request, 'tenant/dashboard.html', {'profile': profile})


# ─── TENANT LIST ─────────────────────────────────────
@login_required(login_url='/')
def tenant_list(request):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    search  = request.GET.get('search', '')
    tenants = TenantProfile.objects.select_related('user').order_by('-created_at')

    if search:
        tenants = tenants.filter(
            models.Q(full_name__icontains=search)       |
            models.Q(phone__icontains=search)           |
            models.Q(room_number__icontains=search)     |
            models.Q(user__email__icontains=search)     |
            models.Q(user__username__icontains=search)
        )

    # Get available rooms for dropdown
    from django.db.models import Count, Q
    available_rooms = Room.objects.annotate(
        occupied_count=Count('tenantprofile', filter=Q(tenantprofile__isnull=False))
    ).filter(
        capacity__gt=models.F('occupied_count')
    ).order_by('floor', 'room_number')

    return render(request, 'admin/tenant_list.html', {
        'tenants': tenants,
        'search' : search,
        'available_rooms': available_rooms,
    })


# ─── ADD TENANT ───────────────────────────────────────
@login_required(login_url='/')
def add_tenant(request):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    if request.method == 'POST':
        username    = request.POST.get('username')
        password    = request.POST.get('password')
        email       = request.POST.get('email')
        full_name   = request.POST.get('full_name')
        phone       = request.POST.get('phone')
        room_id     = request.POST.get('room_number')
        photo       = request.FILES.get('photo')

        if User.objects.filter(username=username).exists():
            tenants = TenantProfile.objects.select_related('user').order_by('-created_at')
            return render(request, 'admin/tenant_list.html', {
                'tenants'       : tenants,
                'add_error'     : 'Username already taken.',
                'show_add_modal': True,
            })

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            is_staff=False,
        )

        # Get the selected room by ID
        selected_room = Room.objects.get(id=room_id)
        
        TenantProfile.objects.create(
            user=user,
            full_name=full_name,
            phone=phone,
            room=selected_room,
            room_number=selected_room.room_number,  # Keep for backward compatibility
            photo=photo,
        )

        return redirect('tenant_list')

    return redirect('tenant_list')

# ... (rest of the code remains the same)

# ─── EDIT TENANT ──────────────────────────────────────
@login_required(login_url='/')
def edit_tenant(request, tenant_id):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    tenant = TenantProfile.objects.get(id=tenant_id)

    if request.method == 'POST':
        tenant.full_name   = request.POST.get('full_name')
        tenant.phone       = request.POST.get('phone')
        tenant.room_number = request.POST.get('room_number')
        tenant.user.email  = request.POST.get('email')

        if request.FILES.get('photo'):
            tenant.photo = request.FILES.get('photo')

        tenant.save()
        tenant.user.save()

        return redirect('tenant_list')

    return redirect('tenant_list')


# ─── DELETE TENANT ────────────────────────────────────
@login_required(login_url='/')
def delete_tenant(request, tenant_id):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    if request.method == 'POST':
        tenant = TenantProfile.objects.get(id=tenant_id)
        tenant.user.delete()

    return redirect('tenant_list')


# ─── ROOM LIST ───────────────────────────────────────
@login_required(login_url='/')
def room_list(request):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')
    rooms = Room.objects.all().order_by('floor', 'room_number')
    return render(request, 'admin/room_list.html', {'rooms': rooms})


# ─── ADD ROOM ────────────────────────────────────────
@login_required(login_url='/')
def add_room(request):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    if request.method == 'POST':
        room_number          = request.POST.get('room_number')
        floor                = request.POST.get('floor')
        capacity             = request.POST.get('capacity')
        monthly_rate         = request.POST.get('monthly_rate')
        photo                = request.FILES.get('photo')
        area                 = request.POST.get('area') or None
        num_cr               = request.POST.get('num_cr', 1)
        bed_type             = request.POST.get('bed_type', 'single')
        has_sink             = request.POST.get('has_sink') == 'on'
        water_included       = request.POST.get('water_included') == 'on'
        electricity_included = request.POST.get('electricity_included') == 'on'
        has_fan              = request.POST.get('has_fan') == 'on'
        has_aircon           = request.POST.get('has_aircon') == 'on'
        has_ref              = request.POST.get('has_ref') == 'on'
        has_tv               = request.POST.get('has_tv') == 'on'
        has_wifi             = request.POST.get('has_wifi') == 'on'

        if Room.objects.filter(room_number=room_number, floor=floor).exists():
            rooms = Room.objects.all().order_by('floor', 'room_number')
            return render(request, 'admin/room_list.html', {
                'rooms'         : rooms,
                'add_error'     : f'Room {floor}-{room_number} already exists.',
                'show_add_modal': True,
            })

        Room.objects.create(
            room_number=room_number,
            floor=floor,
            capacity=capacity,
            monthly_rate=monthly_rate,
            photo=photo,
            area=area,
            num_cr=num_cr,
            bed_type=bed_type,
            has_lababo=has_sink,
            water_included=water_included,
            electricity_included=electricity_included,
            has_fan=has_fan,
            has_aircon=has_aircon,
            has_ref=has_ref,
            has_tv=has_tv,
            has_wifi=has_wifi,
        )

        return redirect('room_list')

    return redirect('room_list')


# ─── EDIT ROOM ───────────────────────────────────────
@login_required(login_url='/')
def edit_room(request, room_id):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    room = Room.objects.get(id=room_id)

    if request.method == 'POST':
        room.room_number         = request.POST.get('room_number')
        room.floor               = request.POST.get('floor')
        room.capacity            = request.POST.get('capacity')
        room.monthly_rate        = request.POST.get('monthly_rate')
        room.area                = request.POST.get('area') or None
        room.num_cr              = request.POST.get('num_cr', 1)
        room.bed_type            = request.POST.get('bed_type', 'single')
        room.has_lababo          = request.POST.get('has_sink') == 'on'
        room.water_included      = request.POST.get('water_included') == 'on'
        room.electricity_included= request.POST.get('electricity_included') == 'on'
        room.has_fan             = request.POST.get('has_fan') == 'on'
        room.has_aircon          = request.POST.get('has_aircon') == 'on'
        room.has_ref             = request.POST.get('has_ref') == 'on'
        room.has_tv              = request.POST.get('has_tv') == 'on'
        room.has_wifi            = request.POST.get('has_wifi') == 'on'

        if request.FILES.get('photo'):
            room.photo = request.FILES.get('photo')

        room.save()
        return redirect('room_list')

    return redirect('room_list')


# ─── DELETE ROOM ─────────────────────────────────────
@login_required(login_url='/')
def delete_room(request, room_id):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    if request.method == 'POST':
        room = Room.objects.get(id=room_id)
        room.delete()

    return redirect('room_list')


# ─── LOGOUT ──────────────────────────────────────────
def logout_view(request):
    logout(request)
    return redirect('login')