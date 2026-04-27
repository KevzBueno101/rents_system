from django import template

register = template.Library()


@register.filter
def activity_icon(action):
    """Get Bootstrap icon class for a given action type."""
    icon_map = {
        'tenant_created': 'bi-person-plus',
        'tenant_updated': 'bi-person-gear',
        'tenant_deleted': 'bi-person-x',
        'room_created': 'bi-door-open',
        'room_updated': 'bi-door-closed',
        'room_deleted': 'bi-door-closed-fill',
        'bill_generated': 'bi-file-earmark-plus',
        'bill_updated': 'bi-file-earmark-pencil',
        'bill_deleted': 'bi-file-earmark-x',
        'bill_sent': 'bi-send',
        'payment_recorded': 'bi-cash-coin',
        'payment_deleted': 'bi-cash-x',
        'admin_created': 'bi-shield-plus',
        'admin_updated': 'bi-shield-gear',
        'admin_deleted': 'bi-shield-x',
        'maintenance_created': 'bi-tools',
        'maintenance_updated': 'bi-gear',
        'maintenance_completed': 'bi-check-circle',
    }
    return icon_map.get(action, 'bi-activity')


@register.filter
def activity_color(action):
    """Get Bootstrap color class for a given action type."""
    color_map = {
        'tenant_created': 'text-primary',
        'tenant_updated': 'text-info',
        'tenant_deleted': 'text-danger',
        'room_created': 'text-primary',
        'room_updated': 'text-info',
        'room_deleted': 'text-danger',
        'bill_generated': 'text-primary',
        'bill_updated': 'text-info',
        'bill_deleted': 'text-danger',
        'bill_sent': 'text-success',
        'payment_recorded': 'text-success',
        'payment_deleted': 'text-danger',
        'admin_created': 'text-primary',
        'admin_updated': 'text-info',
        'admin_deleted': 'text-danger',
        'maintenance_created': 'text-warning',
        'maintenance_updated': 'text-info',
        'maintenance_completed': 'text-success',
    }
    return color_map.get(action, 'text-secondary')
