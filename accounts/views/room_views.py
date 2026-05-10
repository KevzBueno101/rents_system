"""
Room management views: list, add, edit, delete, and feature management.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Max, Q, ProtectedError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..models import Room, Inclusion, Appliance, TenantProfile, RoomImage
from ..activity_utils import log_activity


def room_list(request):
    """List all rooms with search and sorting."""
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

    rooms = Room.objects.prefetch_related('dynamic_inclusions', 'additional_images')

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


@login_required(login_url='/login/')
def tenant_show_rooms(request):
    """Read-only room availability for tenant users."""
    if request.user.is_staff:
        return redirect('room_list')

    profile = TenantProfile.objects.select_related('user', 'room').get(user=request.user)
    search = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'floor')
    order = request.GET.get('order', 'asc')

    valid_sorts = {
        'floor': 'floor',
        'rate': 'monthly_rate',
        'capacity': 'capacity',
        'room_number': 'room_number',
    }
    sort_field = valid_sorts.get(sort_by, 'floor')

    rooms = Room.objects.prefetch_related('dynamic_inclusions').order_by(sort_field, 'room_number')
    if search:
        rooms = rooms.filter(
            Q(room_number__icontains=search) |
            Q(floor__icontains=search) |
            Q(monthly_rate__icontains=search)
        )
    if order == 'desc':
        rooms = rooms.order_by(f'-{sort_field}', 'room_number')

    all_rooms = list(Room.objects.all())
    total_beds = sum(room.capacity for room in all_rooms)
    occupied_beds = sum(room.occupied_beds() for room in all_rooms)

    return render(request, 'tenant/tenant_rooms.html', {
        'profile': profile,
        'rooms': rooms,
        'current_sort': sort_by,
        'current_order': order,
        'search': search,
        'total_beds': total_beds,
        'occupied_beds': occupied_beds,
        'vacant_beds': total_beds - occupied_beds,
        'data': {'room': profile.room},
    })


def add_room(request):
    """Add a new room."""
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    if request.method == 'POST':
        room_number          = request.POST.get('room_number')
        floor                = request.POST.get('floor')
        capacity             = request.POST.get('capacity')
        monthly_rate         = request.POST.get('monthly_rate')
        photos               = request.FILES.getlist('photos')
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

        # Create room first
        room = Room.objects.create(
            room_number=room_number,
            floor=floor,
            capacity=capacity,
            monthly_rate=monthly_rate,
            area=area,
            num_cr=num_cr,
            bed_type=bed_type,
            has_lababo=has_sink,
            water_included=water_included,
            electricity_included=electricity_included,
            has_wifi=has_wifi,
        )
        
        # Handle multiple photos
        for order, photo in enumerate(photos):
            if order == 0:
                # First photo becomes the primary photo
                room.photo = photo
                room.save()
            else:
                # Additional photos go to RoomImage
                RoomImage.objects.create(
                    room=room,
                    image=photo,
                    order=order
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


@login_required(login_url='/admin/login/')
def edit_room(request, room_id):
    """Edit room details (AJAX-enabled)."""
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

        room.save()

        photos = request.FILES.getlist('photos')
        if photos:
            room.photo = photos[0]
            room.save(update_fields=['photo'])

            next_order = (room.additional_images.aggregate(Max('order'))['order__max'] or 0) + 1
            for offset, photo in enumerate(photos[1:]):
                RoomImage.objects.create(
                    room=room,
                    image=photo,
                    order=next_order + offset
                )

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
                'images'            : room.all_images,
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


def delete_room(request, room_id):
    """Delete a room."""
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


@login_required(login_url='/admin/login/')
def get_room_data_api(request, room_id):
    """API endpoint to get room data (AJAX)."""
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
            'images': room.all_images,
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


# ─── ROOM FEATURES (INCLUSIONS & APPLIANCES) ─────────────

@login_required(login_url='/admin/login/')
def add_inclusion(request):
    """Add a new inclusion (AJAX)."""
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


@login_required(login_url='/admin/login/')
def add_appliance(request):
    """Add a new appliance (AJAX)."""
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


@login_required(login_url='/admin/login/')
def get_all_inclusions(request):
    """Get all inclusions (AJAX)."""
    if not request.user.is_staff:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        return redirect('admin_dashboard')
    
    inclusions = list(Inclusion.objects.values('id', 'name'))
    return JsonResponse(inclusions, safe=False)


@login_required(login_url='/admin/login/')
def get_all_appliances(request):
    """Get all appliances (AJAX)."""
    if not request.user.is_staff:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        return redirect('admin_dashboard')
    
    appliances = list(Appliance.objects.values('id', 'name'))
    return JsonResponse(appliances, safe=False)


@login_required(login_url='/admin/login/')
def get_room_features(request):
    """Get inclusions and appliances for a room (AJAX)."""
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


# ─── FEATURE MANAGEMENT PAGE ─────────────────────────────

def manage_features(request):
    """Manage inclusions and appliances page."""
    if not request.user.is_staff:
        return redirect('tenant_dashboard')
    
    inclusions = Inclusion.objects.all().order_by('name')
    appliances = Appliance.objects.all().order_by('name')
    
    return render(request, 'admin/manage_features.html', {
        'inclusions': inclusions,
        'appliances': appliances
    })


@csrf_exempt
@login_required(login_url='/admin/login/')
def add_inclusion_management(request):
    """Add inclusion from management page (AJAX)."""
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


@login_required(login_url='/admin/login/')
def edit_inclusion(request, inclusion_id):
    """Edit inclusion (AJAX)."""
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


@login_required(login_url='/admin/login/')
def delete_inclusion(request, inclusion_id):
    """Delete inclusion (AJAX)."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        inclusion = Inclusion.objects.get(id=inclusion_id)
        inclusion.delete()
        return JsonResponse({'success': True})
    except Inclusion.DoesNotExist:
        return JsonResponse({'error': 'Inclusion not found'}, status=404)


@login_required(login_url='/admin/login/')
def add_appliance_management(request):
    """Add appliance from management page (AJAX)."""
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


@login_required(login_url='/admin/login/')
def edit_appliance(request, appliance_id):
    """Edit appliance (AJAX)."""
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


@login_required(login_url='/admin/login/')
def delete_appliance(request, appliance_id):
    """Delete appliance (AJAX)."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        appliance = Appliance.objects.get(id=appliance_id)
        appliance.delete()
        return JsonResponse({'success': True})
    except Appliance.DoesNotExist:
        return JsonResponse({'error': 'Appliance not found'}, status=404)
