"""
Admin management views: dashboard, list, register, toggle status, delete.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from ..models import AdminProfile
from ..activity_utils import log_activity
from .helpers import parse_phone, get_dashboard_context


def admin_dashboard(request):
    """Admin dashboard with stats and recent activities."""
    if not request.user.is_staff:
        return redirect('tenant_dashboard')
    context = get_dashboard_context()
    from ..activity_utils import get_recent_activities
    context['activities'] = get_recent_activities(limit=3)
    return render(request, 'admin/dashboard.html', context)


def admin_list(request):
    """List all admins with search functionality (Superadmin only)."""
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


def register_admin(request):
    if not request.user.is_superuser:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        username  = request.POST.get('username', '').strip()
        password  = request.POST.get('password', '').strip()
        email     = request.POST.get('email', '').strip()
        full_name = request.POST.get('full_name', '').strip()
        phone_raw = request.POST.get('phone', '').strip()
        phone     = parse_phone(phone_raw)
        photo     = request.FILES.get('photo')

        def render_error(error_msg):
            return render(request, 'admin/admin_list.html', {
                'admins'             : AdminProfile.objects.select_related('user', 'created_by').order_by('-created_at'),
                'register_error'     : error_msg,
                'show_register_modal': True,
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

        if User.objects.filter(username__iexact=username).exists():
            return render_error('Username already taken.')

        if User.objects.filter(email__iexact=email).exists():
            return render_error('This email is already registered. Please use a different email.')

        # ── ALL VALID — CREATE USER & PROFILE ──
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
            created_by=request.user,
        )

        messages.success(request, f'Administrator {full_name} registered.')
        log_activity(
            user=request.user,
            action='admin_created',
            description=f'Created admin account {username}',
            content_type='AdminProfile',
            object_id=admin_profile.id,
        )
        return redirect('admin_list')

    return redirect('admin_list')


def toggle_admin_status(request, user_id):
    """Toggle admin active/inactive status (Superadmin only)."""
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


def delete_admin(request, user_id):
    """Delete an admin account (Superadmin only)."""
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


def audit_trail(request):
    """Display comprehensive audit trail with filtering and pagination (Admin only)."""
    if not request.user.is_staff:
        return redirect('tenant_dashboard')
    
    from django.core.paginator import Paginator
    from ..models import ActivityLog
    from django.contrib.auth.models import User
    from datetime import datetime
    import csv
    from django.http import HttpResponse
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.utils import ImageReader
    import io
    
    # Check for export requests
    export_format = request.GET.get('export', '').lower()
    if export_format in ['csv', 'pdf']:
        return export_audit_trail(request, export_format)
    
    # Get filter parameters
    user_filter = request.GET.get('user', '')
    action_filter = request.GET.get('action', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    content_type_filter = request.GET.get('content_type', '')
    search = request.GET.get('search', '')
    
    # Start with base queryset
    activities = ActivityLog.objects.all().select_related('user').order_by('-timestamp')
    
    # Apply filters safely
    if user_filter and user_filter.isdigit():
        activities = activities.filter(user_id=int(user_filter))
    
    if action_filter:
        activities = activities.filter(action=action_filter)
    
    if content_type_filter:
        activities = activities.filter(content_type__icontains=content_type_filter)
    
    if search:
        activities = activities.filter(description__icontains=search)
    
    # Date range filtering
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            activities = activities.filter(timestamp__date__gte=date_from_obj)
        except ValueError:
            pass  # Invalid date format, ignore filter
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            activities = activities.filter(timestamp__date__lte=date_to_obj)
        except ValueError:
            pass  # Invalid date format, ignore filter
    
    # Pagination (50 records per page)
    paginator = Paginator(activities, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options for dropdowns
    staff_users = User.objects.filter(is_staff=True).order_by('username')
    action_choices = ActivityLog.ACTION_CHOICES
    content_types = ActivityLog.objects.values_list('content_type', flat=True).distinct()
    content_types = [ct for ct in content_types if ct]  # Remove empty values
    
    # Preserve filters in pagination
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    
    context = {
        'page_obj': page_obj,
        'activities': page_obj,
        'staff_users': staff_users,
        'action_choices': action_choices,
        'content_types': content_types,
        'filters': {
            'user': user_filter,
            'action': action_filter,
            'date_from': date_from,
            'date_to': date_to,
            'content_type': content_type_filter,
            'search': search,
        },
        'query_params': query_params.urlencode(),
    }
    
    return render(request, 'admin/audit_trail.html', context)


def export_audit_trail(request, export_format):
    """Export audit trail data to CSV or PDF format (Admin only)."""
    if not request.user.is_staff:
        return redirect('tenant_dashboard')
    
    from ..models import ActivityLog
    from django.contrib.auth.models import User
    from datetime import datetime
    import csv
    from django.http import HttpResponse
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.utils import ImageReader
    import io
    
    # Get filter parameters (same as main view)
    user_filter = request.GET.get('user', '')
    action_filter = request.GET.get('action', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    content_type_filter = request.GET.get('content_type', '')
    search = request.GET.get('search', '')
    
    # Build filtered queryset (same as main view)
    activities = ActivityLog.objects.all().select_related('user').order_by('-timestamp')
    
    if user_filter and user_filter.isdigit():
        activities = activities.filter(user_id=int(user_filter))
    
    if action_filter:
        activities = activities.filter(action=action_filter)
    
    if content_type_filter:
        activities = activities.filter(content_type__icontains=content_type_filter)
    
    if search:
        activities = activities.filter(description__icontains=search)
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            activities = activities.filter(timestamp__date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            activities = activities.filter(timestamp__date__lte=date_to_obj)
        except ValueError:
            pass
    
    # Export based on format
    if export_format == 'csv':
        return export_csv(activities)
    elif export_format == 'pdf':
        return export_pdf(activities)


def export_csv(activities):
    """Export activities to CSV format."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="audit_trail.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'ID', 'User', 'Action', 'Description', 'Content Type', 
        'Object ID', 'Timestamp', 'Date', 'Time'
    ])
    
    # Write data rows
    for activity in activities:
        writer.writerow([
            activity.id,
            activity.user.username if activity.user else 'System',
            activity.get_action_display(),
            activity.description,
            activity.content_type,
            activity.object_id,
            activity.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            activity.timestamp.strftime('%Y-%m-%d'),
            activity.timestamp.strftime('%H:%M:%S'),
        ])
    
    return response


def export_pdf(activities):
    """Export activities to PDF format."""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="audit_trail.pdf"'
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, "Audit Trail Report")
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 70, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    p.drawString(50, height - 85, f"Total Records: {activities.count()}")
    
    # Table headers
    p.setFont("Helvetica-Bold", 9)
    y_position = height - 120
    
    headers = ['ID', 'User', 'Action', 'Description', 'Type', 'Timestamp']
    x_positions = [50, 80, 150, 250, 400, 480]
    
    for i, header in enumerate(headers):
        p.drawString(x_positions[i], y_position, header)
    
    # Table data
    p.setFont("Helvetica", 8)
    y_position -= 15
    
    for activity in activities:
        if y_position < 50:  # New page if needed
            p.showPage()
            y_position = height - 50
            # Redraw headers on new page
            p.setFont("Helvetica-Bold", 9)
            for i, header in enumerate(headers):
                p.drawString(x_positions[i], y_position, header)
            y_position -= 15
            p.setFont("Helvetica", 8)
        
        # Truncate long descriptions
        description = activity.description[:50] + "..." if len(activity.description) > 50 else activity.description
        
        row_data = [
            str(activity.id),
            activity.user.username if activity.user else 'System',
            activity.get_action_display(),
            description,
            activity.content_type or '',
            activity.timestamp.strftime('%m/%d %H:%M')
        ]
        
        for i, data in enumerate(row_data):
            p.drawString(x_positions[i], y_position, data)
        
        y_position -= 12
    
    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response
