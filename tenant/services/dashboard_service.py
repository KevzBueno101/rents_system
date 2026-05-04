from decimal import Decimal

from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch, Sum
from django.utils import timezone

from accounts.models import Bill, Notification, Payment, TenantProfile


def _money(value):
    return value or Decimal("0.00")


def _bill_balance(bill):
    if not bill:
        return Decimal("0.00")
    return _money(bill.total_amount) - _money(bill.paid_amount)


def _notification(level, title, message, icon="bi-info-circle"):
    return {
        "level": level,
        "title": title,
        "message": message,
        "icon": icon,
    }


def get_payment_summary(user):
    tenant = TenantProfile.objects.get(user=user)
    bills = Bill.objects.filter(tenant=tenant)
    total_billed = _money(bills.aggregate(total=Sum("total_amount"))["total"])
    total_paid = _money(Payment.objects.filter(bill__tenant=tenant).aggregate(total=Sum("amount"))["total"])

    return {
        "total_billed": total_billed,
        "total_paid": total_paid,
        "balance": total_billed - total_paid,
    }


def get_notifications(user):
    tenant = TenantProfile.objects.select_related("room").get(user=user)
    today = timezone.localdate()
    notifications = []

    next_bill = (
        Bill.objects.filter(tenant=tenant)
        .exclude(status="paid")
        .order_by("due_date", "-created_at")
        .first()
    )
    if next_bill:
        if next_bill.status == "overdue" or (next_bill.due_date and next_bill.due_date < today):
            notifications.append(
                _notification(
                    "danger",
                    "Payment overdue",
                    f"{next_bill.bill_number} has an outstanding balance of PHP {_bill_balance(next_bill):,.2f}.",
                    "bi-exclamation-triangle",
                )
            )
        elif next_bill.due_date:
            days_left = (next_bill.due_date - today).days
            if days_left <= 3:
                notifications.append(
                    _notification(
                        "warning",
                        "Due date approaching",
                        f"{next_bill.bill_number} is due on {next_bill.due_date:%b %d, %Y}.",
                        "bi-clock-history",
                    )
                )

    latest_payment = (
        Payment.objects.filter(bill__tenant=tenant)
        .select_related("bill")
        .order_by("-payment_date", "-created_at")
        .first()
    )
    if latest_payment:
        notifications.append(
            _notification(
                "success",
                "Latest payment recorded",
                f"PHP {latest_payment.amount:,.2f} was recorded for {latest_payment.bill.bill_number}.",
                "bi-check-circle",
            )
        )

    stored_notifications = Notification.objects.filter(user=user).order_by("-created_at")[:5]
    for item in stored_notifications:
        # Create notification dict but preserve the original object properties
        notification_dict = _notification(
            "info" if item.is_read else "warning",
            item.title,
            item.message,
            "bi-bell",
        )
        # Preserve the original notification object properties
        notification_dict['id'] = item.id
        notification_dict['is_read'] = item.is_read
        notification_dict['created_at'] = item.created_at
        notification_dict['link'] = item.get_absolute_url()
        notifications.append(notification_dict)

    return notifications[:6]


def get_tenant_dashboard_data(user):
    if user.is_staff:
        raise PermissionDenied("Tenant dashboard is only available to tenant users.")

    tenant = TenantProfile.objects.select_related("user", "room").get(user=user)
    payment_prefetch = Prefetch(
        "payments",
        queryset=Payment.objects.order_by("-payment_date", "-created_at"),
    )
    bills = (
        Bill.objects.filter(tenant=tenant)
        .select_related("tenant", "room")
        .prefetch_related(payment_prefetch)
        .order_by("-created_at")
    )
    active_bill = bills.exclude(status="paid").order_by("due_date", "-created_at").first()
    latest_bill = bills.first()
    focus_bill = active_bill or latest_bill

    payment_history = (
        Payment.objects.filter(bill__tenant=tenant)
        .select_related("bill", "bill__tenant", "bill__room")
        .order_by("-payment_date", "-created_at")[:5]
    )
    latest_payment = payment_history[0] if payment_history else None
    latest_receipt = (
        Payment.objects.filter(bill__tenant=tenant)
        .exclude(receipt_image="")
        .exclude(receipt_image__isnull=True)
        .select_related("bill", "bill__tenant", "bill__room")
        .order_by("-payment_date", "-created_at")
        .first()
    )

    summary = get_payment_summary(user)
    due_date = focus_bill.due_date if focus_bill else None
    payment_status = focus_bill.status if focus_bill else "no_bill"
    payment_status_labels = {
        "draft": "Draft",
        "sent": "Sent",
        "partial": "Partial",
        "paid": "Paid",
        "overdue": "Overdue",
        "no_bill": "No bill",
    }

    return {
        "tenant": tenant,
        "balance": summary["balance"],
        "due_date": due_date,
        "payment_status": payment_status,
        "payment_status_label": payment_status_labels.get(payment_status, payment_status.title()),
        "latest_payment": latest_payment,
        "payment_history": payment_history,
        "latest_receipt": latest_receipt,
        "notifications": get_notifications(user),
        "current_bill": focus_bill,
        "room": tenant.room,
        "summary": summary,
        "unread_notifications": Notification.objects.filter(user=user, is_read=False).count(),
    }
