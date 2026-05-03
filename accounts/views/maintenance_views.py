"""
Maintenance and violation views: list, create, update, delete.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from ..models import MaintenanceReport, Violation, TenantProfile
from ..activity_utils import log_activity
from ..services.notification_service import NotificationService


@login_required(login_url='/')
def maintenance_list(request):
    """List all maintenance reports."""
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
    """Create a new maintenance report."""
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
    """Update maintenance report status."""
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
            
            # Create notification for tenant about maintenance update
            try:
                # Debug: Print information to help troubleshoot
                print(f"DEBUG: Creating maintenance notification for report {report_id}")
                print(f"DEBUG: Report tenant: {report.tenant}")
                print(f"DEBUG: Report tenant user: {report.tenant.user if report.tenant else 'None'}")
                print(f"DEBUG: New status: {report.status}")
                
                if report.tenant and report.tenant.user:
                    notification = NotificationService.create_maintenance_notification(
                        tenant_user=report.tenant.user,
                        status=report.status
                    )
                    print(f"DEBUG: Notification created successfully: {notification.id}")
                else:
                    print("DEBUG: No tenant or tenant user found for maintenance report")
                    
            except Exception as e:
                # Log error but don't fail the maintenance update
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to create maintenance notification: {e}")
                print(f"DEBUG: Exception in notification creation: {e}")
            
            messages.success(request, 'Maintenance status updated!')
        except MaintenanceReport.DoesNotExist:
            messages.error(request, 'Maintenance report not found')

    return redirect('maintenance_list')


@login_required(login_url='/')
def delete_maintenance(request, report_id):
    """Delete a maintenance report."""
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
    """List all violations."""
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
    """Create a new violation."""
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
    """Delete a violation."""
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
