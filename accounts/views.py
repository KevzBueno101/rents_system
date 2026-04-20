from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import TenantProfile

# ─── LOGIN ───────────────────────────────────────────
def login_view(request):
    if request.method == 'POST':
        role     = request.POST.get('role')
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Check if role matches
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


# ─── SIGNUP (TENANT ONLY) ─────────────────────────────
def signup_view(request):
    if request.method == 'POST':
        username    = request.POST.get('username')
        password    = request.POST.get('password')
        email       = request.POST.get('email')
        full_name   = request.POST.get('full_name')
        phone       = request.POST.get('phone')
        room_number = request.POST.get('room_number')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return render(request, 'login.html', {
                'signup_error': 'Username already taken. Please choose another.'
            })

        # Create the User
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )

        # Create the TenantProfile
        TenantProfile.objects.create(
            user=user,
            full_name=full_name,
            phone=phone,
            room_number=room_number
        )

        return render(request, 'login.html', {
            'signup_success': 'Account created! You can now log in as Tenant.'
        })

    return redirect('login')


# ─── DASHBOARDS ──────────────────────────────────────
@login_required(login_url='/')
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')
    return render(request, 'admin_dashboard.html')


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