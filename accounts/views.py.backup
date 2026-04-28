from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, ProtectedError, Sum
from django.http import JsonResponse
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.forms import PasswordResetForm
from django.template import loader
from django.utils.safestring import mark_safe
from .models import Inclusion, Appliance, Room, TenantProfile, Bill, Payment, MaintenanceReport, Violation, AdminProfile, ActivityLog, TenantReminder, Notification
from .activity_utils import log_activity, get_recent_activities
import json
import re

# ─── HELPER: clean phone number to digits only ────────
def parse_phone(raw):
    if not raw:
        return None
    digits = re.sub(r"\D", "", str(raw))
    return int(digits) if digits else None



# ─── HELPERS ─────────────────────────────────────────
def get_available_rooms():
    rooms = [r for r in Room.objects.prefetch_related('dynamic_inclusions').order_by('floor', 'room_number') if not r.is_full()]
    # Add dynamic inclusions to each room
    for room in rooms:
        room.dynamic_inclusions_list = [{'id': inc.id, 'name': inc.name} for inc in room.dynamic_inclusions.all()]
    return rooms

def get_dashboard_context():
    all_rooms     = Room.objects.all()
    total_tenants = TenantProfile.objects.count()
    total_beds    = sum(r.capacity for r in all_rooms)
    occupied_beds = sum(r.occupied_beds() for r in all_rooms)

    # Calculate total revenue from all payments
    total_revenue = Payment.objects.aggregate(
        total=Sum('amount')
    )['total'] or 0

    occupied_rooms = [r for r in all_rooms if r.occupied_beds() > 0]
    if len(occupied_rooms) < 3:
        vacant = [r for r in all_rooms if r.occupied_beds() == 0]
        occupied_rooms = occupied_rooms + vacant[:3 - len(occupied_rooms)]

    return {
        'total_tenants' : total_tenants,
        'vacant_rooms'  : sum(1 for r in all_rooms if not r.is_full()),
        'unpaid_bills'  : Bill.objects.exclude(status='paid').count(),
        'open_repairs'  : MaintenanceReport.objects.filter(status='open').count(),
        'recent_tenants': TenantProfile.objects.select_related('user', 'room').order_by('-created_at')[:7],
        'total_beds'    : total_beds,
        'occupied_beds' : occupied_beds,
        'vacant_beds'   : total_beds - occupied_beds,
        'occupancy_rate': (occupied_beds / total_beds * 100) if total_beds > 0 else 0,
        'recent_rooms'  : occupied_rooms[:3],
        'total_rooms': len(all_rooms),
        'total_revenue': total_revenue,
    }


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
                    'error_modal'    : True,
                    'error'          : 'Your account does not match the selected role.',
                    'available_rooms': get_available_rooms(),
                })
        else:
            return render(request, 'login.html', {
                'error_modal'    : True,
                'error'          : 'Invalid username or password.',
                'available_rooms': get_available_rooms(),
            })

    return render(request, 'login.html', {
        'available_rooms': get_available_rooms(),
    })


# ─── SIGNUP ──────────────────────────────────────────
def signup_view(request):
    if request.method == 'POST':
        username  = request.POST.get('username')
        password  = request.POST.get('password')
        email     = request.POST.get('email')
        full_name = request.POST.get('full_name')
        phone     = parse_phone(request.POST.get('phone'))
        room_id   = request.POST.get('room_id')
        photo     = request.FILES.get('photo')

        if not room_id:
            return render(request, 'login.html', {
                'signup_error'   : 'Please select a room.',
                'available_rooms': get_available_rooms(),
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'login.html', {
                'signup_error'   : 'Username already taken. Please choose another.',
                'available_rooms': get_available_rooms(),
            })

        if User.objects.filter(email__iexact=email).exists():
            return render(request, 'login.html', {
                'signup_error'   : 'This email is already registered. Please use a different email.',
                'available_rooms': get_available_rooms(),
            })

        try:
            selected_room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return render(request, 'login.html', {
                'signup_error'   : 'Selected room no longer available.',
                'available_rooms': get_available_rooms(),
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
            room=selected_room,
            room_number=selected_room.room_number,
            photo=photo
        )

        return render(request, 'login.html', {
            'signup_success' : 'Account created! You can now log in as Tenant.',
            'available_rooms': get_available_rooms(),
        })

    return redirect('login')


# ─── REGISTER ADMIN (Superadmin only) ────────────────

def register_admin(request):
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


# ─── ADMIN DASHBOARD ─────────────────────────────────

def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')
    context = get_dashboard_context()
    context['activities'] = get_recent_activities(limit=3)
    return render(request, 'admin/dashboard.html', context)


# ─── ADMIN LIST (Superadmin only) ────────────────────

def admin_list(request):
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


# ─── TOGGLE ADMIN STATUS (Superadmin only) ────────────

def toggle_admin_status(request, user_id):
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


# ─── DELETE ADMIN (Superadmin only) ──────────────────

def delete_admin(request, user_id):
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


# ─── TENANT DASHBOARD ────────────────────────────────

@login_required(login_url='/')
def tenant_dashboard(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    profile = TenantProfile.objects.get(user=request.user)
    return render(request, 'tenant/dashboard.html', {'profile': profile})


# ─── TENANT LIST ─────────────────────────────────────

def tenant_list(request):
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


# ─── ADD TENANT ───────────────────────────────────────

def add_tenant(request):
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


# ─── EDIT TENANT ──────────────────────────────────────

def edit_tenant(request, tenant_id):
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


# ─── DELETE TENANT ────────────────────────────────────

def delete_tenant(request, tenant_id):
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

    return redirect('tenant_list')  # Fixed: was missing


# ─── ROOM LIST ───────────────────────────────────────

def room_list(request):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    search  = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'floor')
    order   = request.GET.get('order', 'asc')

    valid_sorts = {
        'floor'      : 'floor',
        'rate'       : 'monthly_rate',
        'capacity'   : 'capacity',
        'room_number': 'room_number',
    }

    sort_field = valid_sorts.get(sort_by, 'floor')

    rooms = Room.objects.prefetch_related('dynamic_inclusions')

    if search:
        rooms = rooms.filter(
            Q(room_number__icontains=search) |
            Q(floor__icontains=search) |
            Q(monthly_rate__icontains=search)
        )

    if order == 'desc':
        rooms = rooms.order_by(f'-{sort_field}', 'room_number')
    else:
        rooms = rooms.order_by(sort_field, 'room_number')

    # ── calculate BEFORE the loop ──────────────────────
    all_rooms     = Room.objects.all()
    total_beds    = sum(r.capacity for r in all_rooms)
    occupied_beds = sum(r.occupied_beds() for r in all_rooms)
    
    # Add dynamic inclusions list to each room for template display
    for room in rooms:
        inclusions_list = [{'id': inc.id, 'name': inc.name} for inc in room.dynamic_inclusions.all()]
        room.dynamic_inclusions_list = inclusions_list

    return render(request, 'admin/room_list.html', {
        'rooms'        : rooms,
        'current_sort' : sort_by,
        'current_order': order,
        'total_beds'   : total_beds,
        'occupied_beds': occupied_beds,
        'vacant_beds'  : total_beds - occupied_beds,
    })


# ─── ADD ROOM ────────────────────────────────────────

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
        has_wifi             = request.POST.get('has_wifi') == 'on'

        if Room.objects.filter(room_number=room_number, floor=floor).exists():
            rooms = Room.objects.all().order_by('floor', 'room_number')
            return render(request, 'admin/room_list.html', {
                'rooms'         : rooms,
                'add_error'     : f'Room {floor}-{room_number} already exists.',
                'show_add_modal': True,
            })

        room = Room.objects.create(
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
            has_wifi=has_wifi,
        )

        log_activity(
            user=request.user,
            action='room_created',
            description=f'Added room {floor}-{room_number}',
            content_type='Room',
            object_id=room.id
        )

        return redirect('room_list')

    return redirect('room_list')


# ─── EDIT ROOM ───────────────────────────────────────

@login_required(login_url='/')
def edit_room(request, room_id):
    if not request.user.is_staff:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Unauthorized'}, status=403)
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
        room.has_wifi            = request.POST.get('has_wifi') == 'on'

        # Ensure capacity is always an int
        capacity_val = request.POST.get('capacity')
        if capacity_val is not None:
            try:
                room.capacity = int(capacity_val)
            except (ValueError, TypeError):
                room.capacity = 1

        # Handle dynamic inclusions
        room.dynamic_inclusions.clear()
        for key in request.POST:
            if key.startswith('dynamic_inclusion_'):
                inclusion_id = key.split('_')[-1]
                try:
                    inclusion = Inclusion.objects.get(id=inclusion_id)
                    room.dynamic_inclusions.add(inclusion)
                except Inclusion.DoesNotExist:
                    pass

        if request.FILES.get('photo'):
            room.photo = request.FILES.get('photo')

        room.save()

        log_activity(
            user=request.user,
            action='room_updated',
            description=f'Updated room {room.floor}-{room.room_number}',
            content_type='Room',
            object_id=room.id
        )
        
        # Check if this is an AJAX request — return full room data so JS can update the card
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            tenants = list(room.get_tenants().values_list('full_name', flat=True))
            dynamic_inclusions = [inc.name for inc in room.dynamic_inclusions.all()]
            return JsonResponse({
                'success'           : True,
                'id'                : room.id,
                'code'              : room.room_code,
                'floor'             : room.floor,
                'occupied'          : room.occupied_beds(),
                'capacity'          : room.capacity,
                'rate'              : float(room.monthly_rate),
                'status'            : room.status(),
                'photo'             : room.photo.url if room.photo else None,
                'tenants'           : tenants,
                'area'              : float(room.area) if room.area else None,
                'cr'                : room.num_cr,
                'bedtype'           : room.get_bed_type_display(),
                'sink'              : room.has_lababo,
                'water'             : room.water_included,
                'elec'              : room.electricity_included,
                'wifi'              : room.has_wifi,
                'dynamic_inclusions': dynamic_inclusions,
            })
        
        return redirect('room_list')

    return redirect('room_list')


# ─── DELETE ROOM ─────────────────────────────────────
from django.db.models import ProtectedError
from django.contrib import messages


def delete_room(request, room_id):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    if request.method == 'POST':
        room = Room.objects.get(id=room_id)

        # Check if room has tenants before attempting deletion
        if room.occupied_beds() > 0:
            messages.error(request, f'Cannot delete {room.room_code} because it still has tenants assigned.')
            return redirect('room_list')

        try:
            room_code = room.room_code
            room_id_log = room.id
            
            log_activity(
                user=request.user,
                action='room_deleted',
                description=f'Deleted room {room_code}',
                content_type='Room',
                object_id=room_id_log
            )
            
            room.delete()
            messages.success(request, f'{room_code} has been deleted successfully.')
        except ProtectedError:
            messages.error(request, f'Cannot delete {room.room_code} because it still has tenants assigned.')

    return redirect('room_list')


# ─── GET ROOM DATA API (for AJAX updates) ──────────────
@login_required(login_url='/')
def get_room_data_api(request, room_id):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        room = Room.objects.get(id=room_id)
        
        # Get all tenants for this room
        tenants = list(room.get_tenants().values_list('full_name', flat=True))
        
        # Get dynamic inclusions
        dynamic_inclusions = [inc.name for inc in room.dynamic_inclusions.all()]
        
        return JsonResponse({
            'id': room.id,
            'code': room.room_code,
            'floor': room.floor,
            'occupied': room.occupied_beds(),
            'capacity': room.capacity,
            'rate': float(room.monthly_rate),
            'status': room.status(),
            'photo': room.photo.url if room.photo else None,
            'tenants': tenants,
            'area': float(room.area) if room.area else None,
            'cr': room.num_cr,
            'bedtype': room.get_bed_type_display(),
            'sink': room.has_lababo,
            'water': room.water_included,
            'elec': room.electricity_included,
            'wifi': room.has_wifi,
            'dynamic_inclusions': dynamic_inclusions,
        })
    except Room.DoesNotExist:
        return JsonResponse({'error': 'Room not found'}, status=404)


# ─── EDIT PROFILE ────────────────────────────────────

def edit_profile(request):
    if request.method == 'POST':
        username         = request.POST.get('username')
        full_name        = request.POST.get('full_name')
        email            = request.POST.get('email')
        phone            = parse_phone(request.POST.get('phone'))
        current_password = request.POST.get('current_password')
        new_password     = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        photo            = request.FILES.get('photo')

        errors = []

        if current_password and not request.user.check_password(current_password):
            errors.append('Current password is incorrect.')

        if new_password and new_password != confirm_password:
            errors.append('New passwords do not match.')

        if errors:
            return render(request, 'admin/dashboard.html', {
                **get_dashboard_context(),
                'profile_errors'    : errors,
                'show_profile_modal': True,
            })

        user          = request.user
        user.username = username
        user.email    = email
        if new_password:
            user.set_password(new_password)
        user.save()

        try:
            admin_profile = AdminProfile.objects.get(user=user)
        except AdminProfile.DoesNotExist:
            admin_profile = AdminProfile(user=user, created_by=user)

        admin_profile.full_name = full_name
        admin_profile.phone     = phone
        if photo:
            admin_profile.photo = photo
        admin_profile.save()
        return redirect('admin_dashboard')



# ─── PASSWORD RESET VIEWS ─────────────────────────────
class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = '/password-reset/done/'
    form_class = PasswordResetForm
    
    def form_valid(self, form):
        # Check if user exists before sending email
        email = form.cleaned_data['email']
        users = User.objects.filter(email=email)
        
        if not users.exists():
            # Don't reveal if email exists or not for security
            messages.info(self.request, 'If an account with that email exists, a password reset link has been sent.')
            return super().form_valid(form)
        
        return super().form_valid(form)
    
    def send_mail(self, subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name=None):
        """
        Override send_mail to properly handle HTML emails
        """
        from django.template.loader import render_to_string
        from django.core.mail import EmailMultiAlternatives
        
        subject = render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())
        
        # Render HTML email
        html_email = render_to_string(email_template_name, context)
        
        # Create email with HTML content
        email_message = EmailMultiAlternatives(subject, '', from_email, [to_email])
        email_message.attach_alternative(html_email, "text/html")
        email_message.send()


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = '/password-reset/complete/'
    
    def form_valid(self, form):
        messages.success(self.request, 'Your password has been reset successfully. You can now log in with your new password.')
        return super().form_valid(form)


# ─── ADD INCLUSION ───────────────────────────────────
@login_required(login_url='/')
def add_inclusion(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            inclusion, created = Inclusion.objects.get_or_create(name=name)
            if created:
                return JsonResponse({'success': True, 'id': inclusion.id, 'name': inclusion.name})
            else:
                return JsonResponse({'error': 'Inclusion already exists'}, status=400)
        else:
            return JsonResponse({'error': 'Name is required'}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


# ─── ADD APPLIANCE ───────────────────────────────────
@login_required(login_url='/')
def add_appliance(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            appliance, created = Appliance.objects.get_or_create(name=name)
            if created:
                return JsonResponse({'success': True, 'id': appliance.id, 'name': appliance.name})
            else:
                return JsonResponse({'error': 'Appliance already exists'}, status=400)
        else:
            return JsonResponse({'error': 'Name is required'}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


# ─── GET ALL INCLUSIONS ─────────────────────────────
@login_required(login_url='/')
def get_all_inclusions(request):
    if not request.user.is_staff:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        return redirect('admin_dashboard')
    
    inclusions = list(Inclusion.objects.values('id', 'name'))
    return JsonResponse(inclusions, safe=False)


# ─── GET ALL APPLIANCES ─────────────────────────────
@login_required(login_url='/')
def get_all_appliances(request):
    if not request.user.is_staff:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        return redirect('admin_dashboard')
    
    appliances = list(Appliance.objects.values('id', 'name'))
    return JsonResponse(appliances, safe=False)


# ─── GET INCLUSIONS AND APPLIANCES ───────────────────
@login_required(login_url='/')
def get_room_features(request):
    if not request.user.is_staff:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        return redirect('admin_dashboard')
    
    room_id = request.GET.get('room_id')
    if room_id:
        try:
            room = Room.objects.get(id=room_id)
            inclusions = list(room.dynamic_inclusions.values('id', 'name'))
            
            return JsonResponse({
                'inclusions': inclusions
            })
        except Room.DoesNotExist:
            return JsonResponse({'error': 'Room not found'}, status=404)
    
    return JsonResponse({'error': 'Room ID is required'}, status=400)


# ─── MANAGE INCLUSIONS AND APPLIANCES ───────────────────

def manage_features(request):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')
    
    inclusions = Inclusion.objects.all().order_by('name')
    appliances = Appliance.objects.all().order_by('name')
    
    return render(request, 'admin/manage_features.html', {
        'inclusions': inclusions,
        'appliances': appliances
    })


# ─── ADD INCLUSION (MANAGEMENT) ─────────────────────────
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required(login_url='/')
def add_inclusion_management(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            inclusion, created = Inclusion.objects.get_or_create(name=name)
            if created:
                return JsonResponse({
                    'success': True, 
                    'id': inclusion.id, 
                    'name': inclusion.name,
                    'created_at': inclusion.created_at.strftime('%Y-%m-%d %H:%M')
                })
            else:
                return JsonResponse({'error': 'Inclusion already exists'}, status=400)
        else:
            return JsonResponse({'error': 'Name is required'}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


# ─── EDIT INCLUSION ───────────────────────────────────
@login_required(login_url='/')
def edit_inclusion(request, inclusion_id):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        inclusion = Inclusion.objects.get(id=inclusion_id)
    except Inclusion.DoesNotExist:
        return JsonResponse({'error': 'Inclusion not found'}, status=404)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            # Check if name already exists (excluding current inclusion)
            if Inclusion.objects.exclude(id=inclusion_id).filter(name=name).exists():
                return JsonResponse({'error': 'Inclusion with this name already exists'}, status=400)
            
            inclusion.name = name
            inclusion.save()
            return JsonResponse({
                'success': True, 
                'name': inclusion.name,
                'updated_at': inclusion.created_at.strftime('%Y-%m-%d %H:%M')
            })
        else:
            return JsonResponse({'error': 'Name is required'}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


# ─── DELETE INCLUSION ─────────────────────────────────
@login_required(login_url='/')
def delete_inclusion(request, inclusion_id):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        inclusion = Inclusion.objects.get(id=inclusion_id)
        inclusion.delete()
        return JsonResponse({'success': True})
    except Inclusion.DoesNotExist:
        return JsonResponse({'error': 'Inclusion not found'}, status=404)


# ─── ADD APPLIANCE (MANAGEMENT) ─────────────────────────
@login_required(login_url='/')
def add_appliance_management(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            appliance, created = Appliance.objects.get_or_create(name=name)
            if created:
                return JsonResponse({
                    'success': True, 
                    'id': appliance.id, 
                    'name': appliance.name,
                    'created_at': appliance.created_at.strftime('%Y-%m-%d %H:%M')
                })
            else:
                return JsonResponse({'error': 'Appliance already exists'}, status=400)
        else:
            return JsonResponse({'error': 'Name is required'}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


# ─── EDIT APPLIANCE ────────────────────────────────────
@login_required(login_url='/')
def edit_appliance(request, appliance_id):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        appliance = Appliance.objects.get(id=appliance_id)
    except Appliance.DoesNotExist:
        return JsonResponse({'error': 'Appliance not found'}, status=404)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            # Check if name already exists (excluding current appliance)
            if Appliance.objects.exclude(id=appliance_id).filter(name=name).exists():
                return JsonResponse({'error': 'Appliance with this name already exists'}, status=400)
            
            appliance.name = name
            appliance.save()
            return JsonResponse({
                'success': True, 
                'name': appliance.name,
                'updated_at': appliance.created_at.strftime('%Y-%m-%d %H:%M')
            })
        else:
            return JsonResponse({'error': 'Name is required'}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


# ─── DELETE APPLIANCE ─────────────────────────────────
@login_required(login_url='/')
def delete_appliance(request, appliance_id):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        appliance = Appliance.objects.get(id=appliance_id)
        appliance.delete()
        return JsonResponse({'success': True})
    except Appliance.DoesNotExist:
        return JsonResponse({'error': 'Appliance not found'}, status=404)


# ─── BILLING SYSTEM ─────────────────────────────────────

@login_required(login_url='/')
def billing_list(request):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    sort_by = request.GET.get('sort', '-created_at')

    bills = Bill.objects.select_related('tenant', 'tenant__user', 'room').prefetch_related('payments')

    if search:
        bills = bills.filter(
            Q(bill_number__icontains=search) |
            Q(tenant__full_name__icontains=search) |
            Q(tenant__user__username__icontains=search)
        )

    if status_filter:
        bills = bills.filter(status=status_filter)

    bills = bills.order_by(sort_by)

    # Get all tenants for the generate bill modal
    all_tenants = TenantProfile.objects.select_related('user', 'room').filter(room__isnull=False).order_by('full_name')

    # Statistics
    from django.db.models import Sum, Count
    stats = {
        'total_bills': bills.count(),
        'outstanding': bills.filter(status__in=['sent', 'overdue']).aggregate(
            total=Sum('total_amount')
        )['total'] or 0,
        'overdue': bills.filter(status='overdue').aggregate(
            total=Sum('total_amount')
        )['total'] or 0,
        'paid': bills.filter(status='paid').aggregate(
            total=Sum('total_amount')
        )['total'] or 0,
        'partial': bills.filter(status='partial').count(),
        'draft': bills.filter(status='draft').count(),
    }

    return render(request, 'admin/billing_list.html', {
        'bills': bills,
        'stats': stats,
        'search': search,
        'status_filter': status_filter,
        'sort_by': sort_by,
        'all_tenants': all_tenants,
        'activities': get_recent_activities(limit=10),
    })


@login_required(login_url='/')
def generate_bill(request):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    if request.method == 'POST':
        tenant_id = request.POST.get('tenant')
        period_start = request.POST.get('period_start')
        period_end = request.POST.get('period_end')
        due_date = request.POST.get('due_date')
        total_amount = request.POST.get('total_amount')
        notes = request.POST.get('notes', '')
        save_as_draft = request.POST.get('save_as_draft') == 'on'

        try:
            tenant = TenantProfile.objects.get(id=tenant_id)
        except TenantProfile.DoesNotExist:
            messages.error(request, 'Tenant not found')
            return redirect('billing_list')

        from datetime import datetime

        bill = Bill(
            tenant=tenant,
            period_start=datetime.strptime(period_start, '%Y-%m-%d').date() if period_start else None,
            period_end=datetime.strptime(period_end, '%Y-%m-%d').date() if period_end else None,
            due_date=datetime.strptime(due_date, '%Y-%m-%d').date() if due_date else None,
            total_amount=total_amount,
            notes=notes,
            status='draft' if save_as_draft else 'sent'
        )
        bill.save()

        log_activity(
            user=request.user,
            action='bill_generated',
            description=f'Generated bill {bill.bill_number} for {tenant.full_name} (₱{total_amount})',
            content_type='Bill',
            object_id=bill.id
        )

        messages.success(request, f'Bill {bill.bill_number} generated successfully!')
    return redirect('billing_list')


@login_required(login_url='/')
def edit_bill(request, bill_id):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    try:
        bill = Bill.objects.get(id=bill_id)
    except Bill.DoesNotExist:
        messages.error(request, 'Bill not found')
        return redirect('billing_list')

    if request.method == 'POST':
        if bill.status == 'paid':
            messages.error(request, 'Cannot edit paid bills')
            return redirect('billing_list')

        from datetime import datetime

        period_start = request.POST.get('period_start')
        period_end = request.POST.get('period_end')
        due_date = request.POST.get('due_date')

        bill.period_start = datetime.strptime(period_start, '%Y-%m-%d').date() if period_start else None
        bill.period_end = datetime.strptime(period_end, '%Y-%m-%d').date() if period_end else None
        bill.due_date = datetime.strptime(due_date, '%Y-%m-%d').date() if due_date else None
        bill.total_amount = request.POST.get('total_amount')
        bill.notes = request.POST.get('notes', '')
        bill.status = request.POST.get('status', bill.status)
        bill.save()

        log_activity(
            user=request.user,
            action='bill_updated',
            description=f'Updated bill {bill.bill_number} for {bill.tenant.full_name}',
            content_type='Bill',
            object_id=bill.id
        )

        messages.success(request, f'Bill {bill.bill_number} updated successfully!')
        return redirect('view_bill', bill_id=bill.id)

    return redirect('billing_list')


@login_required(login_url='/')
def view_bill(request, bill_id):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    try:
        bill = Bill.objects.select_related('tenant', 'tenant__user', 'room').prefetch_related('payments', 'items').get(id=bill_id)
    except Bill.DoesNotExist:
        return redirect('billing_list')

    return render(request, 'admin/billing_view.html', {'bill': bill})


@login_required(login_url='/')
def delete_bill(request, bill_id):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    if request.method == 'POST':
        try:
            bill = Bill.objects.get(id=bill_id)
            bill_number = bill.bill_number
            tenant_name = bill.tenant.full_name
            bill.delete()
            
            log_activity(
                user=request.user,
                action='bill_deleted',
                description=f'Deleted bill {bill_number} for {tenant_name}',
                content_type='Bill',
                object_id=bill_id
            )
            
            messages.success(request, f'Bill {bill_number} deleted successfully!')
        except Bill.DoesNotExist:
            messages.error(request, 'Bill not found')

    return redirect('billing_list')


@login_required(login_url='/')
def record_payment(request, bill_id):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    try:
        bill = Bill.objects.get(id=bill_id)
    except Bill.DoesNotExist:
        messages.error(request, 'Bill not found')
        return redirect('billing_list')

    if request.method == 'POST':
        amount = request.POST.get('amount')
        payment_date = request.POST.get('payment_date')
        payment_method = request.POST.get('payment_method')
        reference_number = request.POST.get('reference_number', '')
        notes = request.POST.get('notes', '')
        proof = request.FILES.get('proof')

        from datetime import datetime

        payment = Payment.objects.create(
            bill=bill,
            amount=amount,
            payment_date=datetime.strptime(payment_date, '%Y-%m-%d').date() if payment_date else None,
            payment_method=payment_method,
            reference_number=reference_number,
            notes=notes,
            proof=proof
        )

        bill.update_status()

        log_activity(
            user=request.user,
            action='payment_recorded',
            description=f'Recorded payment of ₱{amount} for bill {bill.bill_number}',
            content_type='Payment',
            object_id=payment.id
        )

        messages.success(request, f'Payment of ₱{amount} recorded successfully!')
        return redirect('billing_list')

    return redirect('billing_list')


@login_required(login_url='/')
def delete_payment(request, payment_id):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    try:
        payment = Payment.objects.get(id=payment_id)
        bill = payment.bill
        amount = payment.amount
        payment.delete()
        bill.update_status()
        
        log_activity(
            user=request.user,
            action='payment_deleted',
            description=f'Deleted payment of ₱{amount} for bill {bill.bill_number}',
            content_type='Payment',
            object_id=payment_id
        )
        
        return redirect('view_bill', bill_id=bill.id)
    except Payment.DoesNotExist:
        messages.error(request, 'Payment not found')
        return redirect('billing_list')


@login_required(login_url='/')
def mark_as_sent(request, bill_id):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    try:
        bill = Bill.objects.get(id=bill_id)
        bill.status = 'sent'
        bill.save(update_fields=['status'])
        
        log_activity(
            user=request.user,
            action='bill_sent',
            description=f'Marked bill {bill.bill_number} as sent to {bill.tenant.full_name}',
            content_type='Bill',
            object_id=bill.id
        )
        
        messages.success(request, f'Bill {bill.bill_number} marked as sent!')
    except Bill.DoesNotExist:
        messages.error(request, 'Bill not found')

    return redirect('billing_list')


# ─── TENANT REMINDERS ─────────────────────────────────

@login_required(login_url='/')
def reminder_list(request):
    """List all tenant reminders with filtering"""
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('type', '')

    reminders = TenantReminder.objects.select_related('tenant', 'tenant__user', 'tenant__room').order_by('-created_at')

    if search:
        reminders = reminders.filter(
            Q(title__icontains=search) |
            Q(tenant__full_name__icontains=search) |
            Q(message__icontains=search)
        )

    if status_filter:
        reminders = reminders.filter(status=status_filter)

    if type_filter:
        reminders = reminders.filter(reminder_type=type_filter)

    # Get all tenants for the create reminder modal
    all_tenants = TenantProfile.objects.select_related('user', 'room').filter(room__isnull=False).order_by('full_name')

    return render(request, 'admin/reminder_list.html', {
        'reminders': reminders,
        'search': search,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'available_tenants': all_tenants,
    })


@login_required(login_url='/')
def create_reminder(request):
    """Create a new tenant reminder with optional scheduling"""
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    if request.method == 'POST':
        from .forms import TenantReminderForm
        form = TenantReminderForm(request.POST)
        
        if form.is_valid():
            reminder = form.save(commit=False)
            
            # If no scheduled time, send immediately
            if not reminder.scheduled_at:
                reminder.status = 'sent'
                reminder.is_sent = True
                reminder.sent_at = timezone.now()
                reminder.save()
                
                # Create notification immediately
                Notification.objects.create(
                    user=reminder.tenant.user,
                    title=reminder.title,
                    message=reminder.message
                )
                
                log_activity(
                    user=request.user,
                    action='reminder_created',
                    description=f'Sent reminder "{reminder.title}" to {reminder.tenant.full_name}',
                    content_type='TenantReminder',
                    object_id=reminder.id
                )
                
                messages.success(request, f'Reminder sent to {reminder.tenant.full_name}!')
            else:
                # Schedule for future
                reminder.status = 'pending'
                reminder.save()
                
                log_activity(
                    user=request.user,
                    action='reminder_created',
                    description=f'Scheduled reminder "{reminder.title}" for {reminder.tenant.full_name} at {reminder.scheduled_at}',
                    content_type='TenantReminder',
                    object_id=reminder.id
                )
                
                messages.success(request, f'Reminder scheduled for {reminder.scheduled_at}!')
            
            return redirect('reminder_list')
    else:
        from .forms import TenantReminderForm
        form = TenantReminderForm()

    return render(request, 'admin/reminder_create.html', {'form': form})


@login_required(login_url='/')
def view_reminder(request, reminder_id):
    """View a single reminder details"""
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    try:
        reminder = TenantReminder.objects.select_related('tenant', 'tenant__user', 'tenant__room').get(id=reminder_id)
    except TenantReminder.DoesNotExist:
        messages.error(request, 'Reminder not found')
        return redirect('reminder_list')

    return render(request, 'admin/reminder_view.html', {'reminder': reminder})


@login_required(login_url='/')
def delete_reminder(request, reminder_id):
    """Delete a reminder"""
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    if request.method == 'POST':
        try:
            reminder = TenantReminder.objects.get(id=reminder_id)
            reminder.delete()
            messages.success(request, 'Reminder deleted successfully!')
        except TenantReminder.DoesNotExist:
            messages.error(request, 'Reminder not found')

    return redirect('reminder_list')


@login_required(login_url='/')
def send_reminder_now(request, reminder_id):
    """Manually trigger a scheduled reminder to send now"""
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    try:
        reminder = TenantReminder.objects.get(id=reminder_id)
        reminder.mark_as_sent()
        
        log_activity(
            user=request.user,
            action='reminder_sent',
            description=f'Manually sent reminder "{reminder.title}" to {reminder.tenant.full_name}',
            content_type='TenantReminder',
            object_id=reminder.id
        )
        
        messages.success(request, f'Reminder sent to {reminder.tenant.full_name}!')
    except TenantReminder.DoesNotExist:
        messages.error(request, 'Reminder not found')

    return redirect('reminder_list')


# ─── NOTIFICATIONS (TENANT SIDE - FUTURE READY) ─────────

@login_required(login_url='/')
def notification_list(request):
    """List notifications for the current user (future-ready for tenant dashboard)"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'tenant/notifications.html', {
        'notifications': notifications,
        'unread_count': notifications.filter(is_read=False).count()
    })


@login_required(login_url='/')
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save(update_fields=['is_read'])
    except Notification.DoesNotExist:
        pass
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('notification_list')


@login_required(login_url='/')
def mark_all_notifications_read(request):
    """Mark all notifications as read for the current user"""
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('notification_list')


# ─── MAINTENANCE ─────────────────────────────────────

@login_required(login_url='/')
def maintenance_list(request):
    """List all maintenance reports"""
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    status_filter = request.GET.get('status', '')
    
    reports = MaintenanceReport.objects.select_related('tenant', 'tenant__user', 'tenant__room').order_by('-created_at')

    if status_filter:
        reports = reports.filter(status=status_filter)

    # Get all tenants for the create maintenance modal
    tenants = TenantProfile.objects.select_related('user', 'room').filter(room__isnull=False).order_by('full_name')

    return render(request, 'admin/maintenance_list.html', {
        'reports': reports,
        'status_filter': status_filter,
        'tenants': tenants,
    })


@login_required(login_url='/')
def create_maintenance(request):
    """Create a new maintenance report"""
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    if request.method == 'POST':
        tenant_id = request.POST.get('tenant')
        description = request.POST.get('description')
        
        try:
            tenant = TenantProfile.objects.get(id=tenant_id)
            report = MaintenanceReport.objects.create(
                tenant=tenant,
                description=description
            )
            
            log_activity(
                user=request.user,
                action='maintenance_created',
                description=f'Created maintenance report for {tenant.full_name}',
                content_type='MaintenanceReport',
                object_id=report.id
            )
            
            messages.success(request, 'Maintenance report created successfully!')
        except TenantProfile.DoesNotExist:
            messages.error(request, 'Tenant not found')
        
        return redirect('maintenance_list')

    tenants = TenantProfile.objects.select_related('user', 'room').filter(room__isnull=False).order_by('full_name')
    return render(request, 'admin/maintenance_create.html', {'tenants': tenants})


@login_required(login_url='/')
def update_maintenance_status(request, report_id):
    """Update maintenance report status"""
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    if request.method == 'POST':
        try:
            report = MaintenanceReport.objects.get(id=report_id)
            old_status = report.status
            report.status = request.POST.get('status')
            report.save()
            
            log_activity(
                user=request.user,
                action='maintenance_updated',
                description=f'Updated maintenance status from {old_status} to {report.status}',
                content_type='MaintenanceReport',
                object_id=report.id
            )
            
            messages.success(request, 'Maintenance status updated!')
        except MaintenanceReport.DoesNotExist:
            messages.error(request, 'Maintenance report not found')

    return redirect('maintenance_list')


@login_required(login_url='/')
def delete_maintenance(request, report_id):
    """Delete a maintenance report"""
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    if request.method == 'POST':
        try:
            report = MaintenanceReport.objects.get(id=report_id)
            report.delete()
            messages.success(request, 'Maintenance report deleted!')
        except MaintenanceReport.DoesNotExist:
            messages.error(request, 'Maintenance report not found')

    return redirect('maintenance_list')


# ─── VIOLATIONS ───────────────────────────────────────

@login_required(login_url='/')
def violation_list(request):
    """List all violations"""
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    violations = Violation.objects.select_related('tenant', 'tenant__user', 'tenant__room').order_by('-date')
    
    # Get all tenants for the create violation modal
    tenants = TenantProfile.objects.select_related('user', 'room').filter(room__isnull=False).order_by('full_name')
    
    return render(request, 'admin/violation_list.html', {
        'violations': violations,
        'tenants': tenants,
    })


@login_required(login_url='/')
def create_violation(request):
    """Create a new violation"""
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    if request.method == 'POST':
        tenant_id = request.POST.get('tenant')
        description = request.POST.get('description')
        date = request.POST.get('date')
        
        try:
            tenant = TenantProfile.objects.get(id=tenant_id)
            Violation.objects.create(
                tenant=tenant,
                description=description,
                date=date
            )
            
            messages.success(request, 'Violation recorded successfully!')
        except TenantProfile.DoesNotExist:
            messages.error(request, 'Tenant not found')
        
        return redirect('violation_list')

    tenants = TenantProfile.objects.select_related('user', 'room').filter(room__isnull=False).order_by('full_name')
    return render(request, 'admin/violation_create.html', {'tenants': tenants})


@login_required(login_url='/')
def delete_violation(request, violation_id):
    """Delete a violation"""
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    if request.method == 'POST':
        try:
            violation = Violation.objects.get(id=violation_id)
            violation.delete()
            messages.success(request, 'Violation deleted!')
        except Violation.DoesNotExist:
            messages.error(request, 'Violation not found')

    return redirect('violation_list')


# ─── LOGOUT ──────────────────────────────────────────
def logout_view(request):
    logout(request)
    return redirect('login')
