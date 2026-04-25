from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.forms import PasswordResetForm
from django.template import loader
from .models import Inclusion, Appliance, Room, TenantProfile, Room, Bill, MaintenanceReport, Violation, AdminProfile


# ─── HELPERS ─────────────────────────────────────────
def get_available_rooms():
    rooms = [r for r in Room.objects.all().order_by('floor', 'room_number') if not r.is_full()]
    # Add dynamic inclusions and appliances to each room
    for room in rooms:
        room.dynamic_inclusions_list = [{'id': inc.id, 'name': inc.name} for inc in room.dynamic_inclusions.all()]
        room.dynamic_appliances_list = [{'id': app.id, 'name': app.name} for app in room.dynamic_appliances.all()]
    return rooms

def get_dashboard_context():
    all_rooms     = Room.objects.all()
    total_tenants = TenantProfile.objects.count()
    total_beds    = sum(r.capacity for r in all_rooms)
    occupied_beds = sum(r.occupied_beds() for r in all_rooms)
    

    occupied_rooms = [r for r in all_rooms if r.occupied_beds() > 0]
    if len(occupied_rooms) < 3:
        vacant = [r for r in all_rooms if r.occupied_beds() == 0]
        occupied_rooms = occupied_rooms + vacant[:3 - len(occupied_rooms)]

    return {
        'total_tenants' : total_tenants,
        'vacant_rooms'  : sum(1 for r in all_rooms if not r.is_full()),
        'unpaid_bills'  : Bill.objects.filter(is_paid=False).count(),
        'open_repairs'  : MaintenanceReport.objects.filter(status='open').count(),
        'recent_tenants': TenantProfile.objects.select_related('user', 'room').order_by('-created_at')[:5],
        'total_beds'    : total_beds,
        'occupied_beds' : occupied_beds,
        'vacant_beds'   : total_beds - occupied_beds,
        'occupancy_rate': (occupied_beds / total_beds * 100) if total_beds > 0 else 0,
        'recent_rooms'  : occupied_rooms[:3],
        'total_rooms': len(all_rooms),
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
        phone     = request.POST.get('phone')
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
                **get_dashboard_context(),
                'register_error'     : 'Username already taken.',
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
            photo=photo,
            created_by=request.user
        )

        return render(request, 'admin/dashboard.html', {
            **get_dashboard_context(),
            'register_success': f'Admin account for {full_name} created successfully!',
        })

    return redirect('admin_dashboard')


# ─── ADMIN DASHBOARD ─────────────────────────────────
@login_required(login_url='/')
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')
    return render(request, 'admin/dashboard.html', get_dashboard_context())


# ─── ADMIN LIST (Superadmin only) ────────────────────
@login_required(login_url='/')
def admin_list(request):
    if not request.user.is_superuser:
        return redirect('admin_dashboard')

    admins = AdminProfile.objects.select_related('user', 'created_by').order_by('-created_at')
    return render(request, 'admin/admin_list.html', {'admins': admins})


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
    tenants = TenantProfile.objects.select_related('user', 'room').order_by('-created_at')

    if search:
        tenants = tenants.filter(
            models.Q(full_name__icontains=search)   |
            models.Q(phone__icontains=search)       |
            models.Q(room_number__icontains=search) |
            models.Q(user__email__icontains=search) |
            models.Q(user__username__icontains=search)
        )

    return render(request, 'admin/tenant_list.html', {
        'tenants'        : tenants,
        'search'         : search,
        'available_rooms': get_available_rooms(),
    })


# ─── ADD TENANT ───────────────────────────────────────
@login_required(login_url='/')
def add_tenant(request):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    if request.method == 'POST':
        username  = request.POST.get('username')
        password  = request.POST.get('password')
        email     = request.POST.get('email')
        full_name = request.POST.get('full_name')
        phone     = request.POST.get('phone')
        room_id   = request.POST.get('room_id')
        photo     = request.FILES.get('photo')

        if User.objects.filter(username=username).exists():
            return render(request, 'admin/tenant_list.html', {
                'tenants'        : TenantProfile.objects.select_related('user', 'room').order_by('-created_at'),
                'add_error'      : 'Username already taken.',
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

        TenantProfile.objects.create(
            user=user,
            full_name=full_name,
            phone=phone,
            room=selected_room,
            room_number=selected_room.room_number,
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
        tenant.full_name  = request.POST.get('full_name')
        tenant.phone      = request.POST.get('phone')
        tenant.user.email = request.POST.get('email')

        # Fixed: update room FK properly
        room_id = request.POST.get('room_id')
        if room_id:
            try:
                selected_room      = Room.objects.get(id=room_id)
                tenant.room        = selected_room
                tenant.room_number = selected_room.room_number
            except Room.DoesNotExist:
                pass

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

    return redirect('tenant_list')  # Fixed: was missing


# ─── ROOM LIST ───────────────────────────────────────
@login_required(login_url='/')
def room_list(request):
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    sort_by = request.GET.get('sort', 'floor')
    order   = request.GET.get('order', 'asc')

    valid_sorts = {
        'floor'      : 'floor',
        'rate'       : 'monthly_rate',
        'capacity'   : 'capacity',
        'room_number': 'room_number',
    }

    sort_field = valid_sorts.get(sort_by, 'floor')

    if order == 'desc':
        rooms = Room.objects.all().order_by(f'-{sort_field}', 'room_number')
    else:
        rooms = Room.objects.all().order_by(sort_field, 'room_number')

    return render(request, 'admin/room_list.html', {
        'rooms'        : rooms,
        'current_sort' : sort_by,
        'current_order': order,
    })


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

        # Handle dynamic appliances
        room.dynamic_appliances.clear()
        for key in request.POST:
            if key.startswith('dynamic_appliance_'):
                appliance_id = key.split('_')[-1]
                try:
                    appliance = Appliance.objects.get(id=appliance_id)
                    room.dynamic_appliances.add(appliance)
                except Appliance.DoesNotExist:
                    pass

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


# ─── EDIT PROFILE ────────────────────────────────────
@login_required(login_url='/')
def edit_profile(request):
    if request.method == 'POST':
        username         = request.POST.get('username')
        full_name        = request.POST.get('full_name')
        email            = request.POST.get('email')
        phone            = request.POST.get('phone')
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
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    inclusions = list(Inclusion.objects.values('id', 'name'))
    return JsonResponse(inclusions, safe=False)


# ─── GET ALL APPLIANCES ─────────────────────────────
@login_required(login_url='/')
def get_all_appliances(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    appliances = list(Appliance.objects.values('id', 'name'))
    return JsonResponse(appliances, safe=False)


# ─── GET INCLUSIONS AND APPLIANCES ───────────────────
@login_required(login_url='/')
def get_room_features(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    room_id = request.GET.get('room_id')
    if room_id:
        try:
            room = Room.objects.get(id=room_id)
            inclusions = list(room.dynamic_inclusions.values('id', 'name'))
            appliances = list(room.dynamic_appliances.values('id', 'name'))
            
            return JsonResponse({
                'inclusions': inclusions,
                'appliances': appliances
            })
        except Room.DoesNotExist:
            return JsonResponse({'error': 'Room not found'}, status=404)
    
    return JsonResponse({'error': 'Room ID is required'}, status=400)


# ─── MANAGE INCLUSIONS AND APPLIANCES ───────────────────
@login_required(login_url='/')
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


# ─── LOGOUT ──────────────────────────────────────────
def logout_view(request):
    logout(request)
    return redirect('login')