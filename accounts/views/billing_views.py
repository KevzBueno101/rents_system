"""
Billing and payment views: list, generate, edit, view, delete, record payment.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from ..models import Bill, Payment, TenantProfile
from ..activity_utils import log_activity, get_recent_activities


@login_required(login_url='/')
def billing_list(request):
    """List all bills with filtering and statistics."""
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
    """Generate a new bill."""
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
    """Edit an existing bill."""
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
    """View bill details."""
    if not request.user.is_staff:
        return redirect('tenant_dashboard')

    try:
        bill = Bill.objects.select_related('tenant', 'tenant__user', 'room').prefetch_related('payments', 'items').get(id=bill_id)
    except Bill.DoesNotExist:
        return redirect('billing_list')

    return render(request, 'admin/billing_view.html', {'bill': bill})


@login_required(login_url='/')
def delete_bill(request, bill_id):
    """Delete a bill."""
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
    """Record a payment for a bill."""
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
            description=f'Recorded payment of ₱{amount} from {bill.tenant.full_name}',
            content_type='Payment',
            object_id=payment.id
        )

        messages.success(request, f'Payment of ₱{amount} recorded successfully!')
        return redirect('billing_list')

    return redirect('billing_list')


@login_required(login_url='/')
def delete_payment(request, payment_id):
    """Delete a payment."""
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
            description=f'Deleted payment of ₱{amount} from {bill.tenant.full_name}',
            content_type='Payment',
            object_id=payment_id
        )
        
        return redirect('view_bill', bill_id=bill.id)
    except Payment.DoesNotExist:
        messages.error(request, 'Payment not found')
        return redirect('billing_list')


@login_required(login_url='/')
def mark_as_sent(request, bill_id):
    """Mark a bill as sent."""
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
