"""
Reminder and notification views: list, create, view, delete, send, mark read.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from ..models import TenantReminder, Notification, TenantProfile
from ..activity_utils import log_activity


@login_required(login_url='/admin/login/')
def reminder_list(request):
    """List all tenant reminders with filtering."""
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


@login_required(login_url='/admin/login/')
def create_reminder(request):
    """Create a new tenant reminder with optional scheduling."""
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    if request.method == 'POST':
        from ..forms import TenantReminderForm
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
        from ..forms import TenantReminderForm
        form = TenantReminderForm()

    return render(request, 'admin/reminder_create.html', {'form': form})


@login_required(login_url='/admin/login/')
def view_reminder(request, reminder_id):
    """View a single reminder details."""
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    try:
        reminder = TenantReminder.objects.select_related('tenant', 'tenant__user', 'tenant__room').get(id=reminder_id)
    except TenantReminder.DoesNotExist:
        messages.error(request, 'Reminder not found')
        return redirect('reminder_list')

    return render(request, 'admin/reminder_view.html', {'reminder': reminder})


@login_required(login_url='/admin/login/')
def delete_reminder(request, reminder_id):
    """Delete a reminder."""
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


@login_required(login_url='/admin/login/')
def send_reminder_now(request, reminder_id):
    """Manually trigger a scheduled reminder to send now."""
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

@login_required(login_url='/login/')
def notification_list(request):
    """List notifications for the current user with enhanced context."""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Enhanced context for better template rendering
    context = {
        'notifications': notifications,
        'unread_count': notifications.filter(is_read=False).count(),
        'total_count': notifications.count(),
        'page_title': 'Notifications',
        'breadcrumb': [
            {'title': 'Dashboard', 'url': 'tenant_dashboard'},
            {'title': 'Notifications', 'url': None}
        ]
    }
    
    return render(request, 'tenant/notifications.html', context)


@login_required(login_url='/login/')
def mark_notification_read(request, notification_id):
    """Mark a notification as read."""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save(update_fields=['is_read'])
    except Notification.DoesNotExist:
        pass
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('notification_list')


@login_required(login_url='/login/')
def mark_all_notifications_read(request):
    """Mark all notifications as read for the current user."""
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('notification_list')
