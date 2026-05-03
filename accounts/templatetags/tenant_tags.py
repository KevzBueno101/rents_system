"""
Template tags for tenant-related functionality.
"""
from django import template
from ..models import Bill

register = template.Library()


@register.simple_tag
def get_tenant_status(tenant):
    """Get the latest bill status for a tenant."""
    if not tenant:
        return None
    
    latest_bill = Bill.objects.filter(tenant=tenant).order_by('-created_at').first()
    if latest_bill:
        return latest_bill.status
    return None
