from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import TenantProfile, Room, Bill, MaintenanceReport, Violation, AdminProfile
from django.db import models


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

    return render(request, 'login.html')


# ─── SIGNUP ──────────────────────────────────────────
def signup_view(request):
    if request.method == 'POST':
        username    = request.POST.get('username')
        password    = request.POST.get('password')
        email       = request.POST.get('email')
        full_name   = request.POST.get('full_name')
        phone       = request.POST.get('phone')
        room_number = request.POST.get('room_number')
        photo       = request.FILES.get('photo')

        if User.objects.filter(username=username).exists():
            return render(request, 'login.html', {
                'signup_error': 'Username already taken. Please choose another.'
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
            room_number=room_number,
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

    total_tenants  = TenantProfile.objects.count()
    all_rooms      = Room.objects.all()
    vacant_rooms   = sum(1 for r in all_rooms if not r.is_full())
    unpaid_bills   = Bill.objects.filter(is_paid=False).count()
    open_repairs   = MaintenanceReport.objects.filter(status='open').count()
    recent_tenants = TenantProfile.objects.order_by('-created_at')[:5]
    total_beds     = sum(r.capacity for r in all_rooms)
    vacant_beds    = total_beds - TenantProfile.objects.count()

    # ← NEW — get occupied rooms, minimum 3
    occupied_rooms = [r for r in all_rooms if r.occupied_beds() > 0]
    if len(occupied_rooms) < 3:
        # fill remaining slots with vacant rooms
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
        'recent_rooms'  : occupied_rooms[:3],  # ← NEW
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

    search = request.GET.get('search', '')  # ← NEW

    tenants = TenantProfile.objects.select_related('user').order_by('-created_at')

    if search:
        tenants = tenants.filter(
            models.Q(full_name__icontains=search)    |
            models.Q(phone__icontains=search)        |
            models.Q(room_number__icontains=search)  |
            models.Q(user__email__icontains=search)  |
            models.Q(user__username__icontains=search)
        )

    return render(request, 'admin/tenant_list.html', {
        'tenants': tenants,
        'search' : search,   # ← para ma-retain ang search value
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
        room_number = request.POST.get('room_number')
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

        TenantProfile.objects.create(
            user=user,
            full_name=full_name,
            phone=phone,
            room_number=room_number,
            photo=photo,
        )

        return redirect('tenant_list')

    return redirect('tenant_list')


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


# ─── LOGOUT ──────────────────────────────────────────
def logout_view(request):
    logout(request)
    return redirect('login')


# ─── ROOM LIST ───────────────────────────────────────
@login_required(login_url='/')
def room_list(request):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')
    rooms = Room.objects.all().order_by('room_number')
    return render(request, 'admin/room_list.html', {'rooms': rooms})


# ─── ADD ROOM ────────────────────────────────────────
@login_required(login_url='/')
@login_required(login_url='/')
def add_room(request):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    if request.method == 'POST':
        room_number  = request.POST.get('room_number')
        capacity     = request.POST.get('capacity')
        monthly_rate = request.POST.get('monthly_rate')
        photo        = request.FILES.get('photo')  

        if Room.objects.filter(room_number=room_number).exists():
            rooms = Room.objects.all().order_by('room_number')
            return render(request, 'admin/room_list.html', {
                'rooms'         : rooms,
                'add_error'     : f'Room {room_number} already exists.',
                'show_add_modal': True,
            })

        Room.objects.create(
            room_number=room_number,
            capacity=capacity,
            monthly_rate=monthly_rate,
            photo=photo,  
        )

        return redirect('room_list')

    return redirect('room_list')
# ─── ADD ROOM PHOTO ────────────────────────────────────────
@login_required(login_url='/')
def edit_room(request, room_id):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    room = Room.objects.get(id=room_id)

    if request.method == 'POST':
        room.room_number  = request.POST.get('room_number')
        room.capacity     = request.POST.get('capacity')
        room.monthly_rate = request.POST.get('monthly_rate')

        if request.FILES.get('photo'):   # ← NEW
            room.photo = request.FILES.get('photo')

        room.save()
        return redirect('room_list')

    return redirect('room_list')


# ─── EDIT ROOM ───────────────────────────────────────
@login_required(login_url='/')
def edit_room(request, room_id):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    room = Room.objects.get(id=room_id)

    if request.method == 'POST':
        room.room_number  = request.POST.get('room_number')
        room.capacity     = request.POST.get('capacity')
        room.monthly_rate = request.POST.get('monthly_rate')
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

@login_required(login_url='/')
def add_room(request):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    if request.method == 'POST':
        room_number  = request.POST.get('room_number')
        floor        = request.POST.get('floor')
        capacity     = request.POST.get('capacity')
        monthly_rate = request.POST.get('monthly_rate')
        photo        = request.FILES.get('photo')
        area         = request.POST.get('area') or None
        num_cr       = request.POST.get('num_cr', 1)
        bed_type     = request.POST.get('bed_type', 'single')
        has_lababo   = request.POST.get('has_lababo') == 'on'
        water_included       = request.POST.get('water_included') == 'on'
        electricity_included = request.POST.get('electricity_included') == 'on'
        has_fan    = request.POST.get('has_fan') == 'on'
        has_aircon = request.POST.get('has_aircon') == 'on'
        has_ref    = request.POST.get('has_ref') == 'on'
        has_tv     = request.POST.get('has_tv') == 'on'
        has_wifi   = request.POST.get('has_wifi') == 'on'

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
            has_lababo=has_lababo,
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


@login_required(login_url='/')
def edit_room(request, room_id):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    room = Room.objects.get(id=room_id)

    if request.method == 'POST':
        room.room_number  = request.POST.get('room_number')
        room.floor        = request.POST.get('floor')
        room.capacity     = request.POST.get('capacity')
        room.monthly_rate = request.POST.get('monthly_rate')
        room.area         = request.POST.get('area') or None
        room.num_cr       = request.POST.get('num_cr', 1)
        room.bed_type     = request.POST.get('bed_type', 'single')
        room.has_lababo   = request.POST.get('has_lababo') == 'on'
        room.water_included       = request.POST.get('water_included') == 'on'
        room.electricity_included = request.POST.get('electricity_included') == 'on'
        room.has_fan    = request.POST.get('has_fan') == 'on'
        room.has_aircon = request.POST.get('has_aircon') == 'on'
        room.has_ref    = request.POST.get('has_ref') == 'on'
        room.has_tv     = request.POST.get('has_tv') == 'on'
        room.has_wifi   = request.POST.get('has_wifi') == 'on'

        if request.FILES.get('photo'):
            room.photo = request.FILES.get('photo')

        room.save()
        return redirect('room_list')

    return redirect('room_list')

@login_required(login_url='/')
def edit_room(request, room_id):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    room = Room.objects.get(id=room_id)

    if request.method == 'POST':
        room.room_number  = request.POST.get('room_number')
        room.floor        = request.POST.get('floor')
        room.capacity     = request.POST.get('capacity')
        room.monthly_rate = request.POST.get('monthly_rate')

        if request.FILES.get('photo'):
            room.photo = request.FILES.get('photo')

        room.save()
        return redirect('room_list')

    return redirect('room_list')
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    room = Room.objects.get(id=room_id)

    if request.method == 'POST':
        room.room_number  = request.POST.get('room_number')
        room.floor        = request.POST.get('floor')
        room.position     = request.POST.get('position')
        room.capacity     = request.POST.get('capacity')
        room.monthly_rate = request.POST.get('monthly_rate')

        if request.FILES.get('photo'):
            room.photo = request.FILES.get('photo')

        room.save()
        return redirect('room_list')

    return redirect('room_list')