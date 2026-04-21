from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import TenantProfile, Room, Bill, MaintenanceReport, Violation, AdminProfile


# ─── LOGIN ───────────────────────────────────────────
def login_view(request):
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
        photo       = request.FILES.get('photo')  # ← NEW

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
            photo=photo  # ← NEW
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
        photo     = request.FILES.get('photo')  # ← NEW

        if User.objects.filter(username=username).exists():
            return render(request, 'admin_dashboard.html', {
                'register_error': 'Username already taken.',
                'show_register_modal': True,
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
            photo=photo,  # ← NEW
            created_by=request.user
        )

        return render(request, 'admin_dashboard.html', {
            'register_success': f'Admin account for {full_name} created successfully!',
            'total_tenants' : TenantProfile.objects.count(),
            'vacant_rooms'  : sum(1 for r in Room.objects.all() if not r.is_full()),
            'unpaid_bills'  : Bill.objects.filter(is_paid=False).count(),
            'open_repairs'  : MaintenanceReport.objects.filter(status='open').count(),
            'recent_tenants': TenantProfile.objects.order_by('-created_at')[:5],
        })

    return redirect('admin_dashboard')
# ─── ADMIN DASHBOARD ─────────────────────────────────
@login_required(login_url='/')
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    total_tenants  = TenantProfile.objects.count()
    vacant_rooms   = sum(1 for r in Room.objects.all() if not r.is_full())
    unpaid_bills   = Bill.objects.filter(is_paid=False).count()
    open_repairs   = MaintenanceReport.objects.filter(status='open').count()
    recent_tenants = TenantProfile.objects.order_by('-created_at')[:5]

    return render(request, 'admin_dashboard.html', {
        'total_tenants' : total_tenants,
        'vacant_rooms'  : vacant_rooms,
        'unpaid_bills'  : unpaid_bills,
        'open_repairs'  : open_repairs,
        'recent_tenants': recent_tenants,
    })


# ─── ADMIN LIST (Superadmin only) ────────────────────
@login_required(login_url='/')
def admin_list(request):
    if not request.user.is_superuser:
        return redirect('admin_dashboard')

    admins = AdminProfile.objects.select_related('user', 'created_by').order_by('-created_at')

    return render(request, 'admin_list.html', {
        'admins': admins,
    })


# ─── TOGGLE ADMIN STATUS (Superadmin only) ────────────
@login_required(login_url='/')
def toggle_admin_status(request, user_id):
    if not request.user.is_superuser:
        return redirect('admin_dashboard')

    from django.contrib.auth.models import User as AuthUser
    admin_user = AuthUser.objects.get(id=user_id)
    admin_user.is_active = not admin_user.is_active
    admin_user.save()

    return redirect('admin_list')


# ─── TENANT DASHBOARD ────────────────────────────────
@login_required(login_url='/')
def tenant_dashboard(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    profile = TenantProfile.objects.get(user=request.user)
    return render(request, 'tenant_dashboard.html', {'profile': profile})

# ─── LOGOUT ──────────────────────────────────────────
def logout_view(request):
    logout(request)
    return redirect('login')


# ─── DELETE ADMIN (Superadmin only) ──────────────────
@login_required(login_url='/')
def delete_admin(request, user_id):
    if not request.user.is_superuser:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        from django.contrib.auth.models import User as AuthUser
        admin_user = AuthUser.objects.get(id=user_id)
        admin_user.delete()  # deletes User + AdminProfile (cascade)

    return redirect('admin_list')


# ─── TENANT LIST ─────────────────────────────────────
@login_required(login_url='/')
def tenant_list(request):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')
    tenants = TenantProfile.objects.select_related('user').order_by('-created_at')
    return render(request, 'tenant_list.html', {'tenants': tenants})


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
            return render(request, 'tenant_list.html', {
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
        tenant.user.delete()  # deletes User + TenantProfile (cascade)

    return redirect('tenant_list')