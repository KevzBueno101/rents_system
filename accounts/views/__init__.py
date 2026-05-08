"""
Views module - backward compatible imports.
All views are now organized in separate modules but can still be imported from here.
"""

# Import from auth_views
from .auth_views import (
    login_view,
    signup_view,
    logout_view,
    edit_profile,
    CustomPasswordResetView,
    custom_password_reset_confirm,
)

# Import from admin_views
from .admin_views import (
    admin_dashboard,
    admin_list,
    register_admin,
    toggle_admin_status,
    delete_admin,
)

# Import from tenant_views
from .tenant_views import (
    tenant_dashboard,
    tenant_bills,
    tenant_reports,
    tenant_submit_maintenance,
    tenant_submit_violation,
    tenant_list,
    add_tenant,
    edit_tenant,
    delete_tenant,
)

# Import from room_views
from .room_views import (
    room_list,
    tenant_show_rooms,
    add_room,
    edit_room,
    delete_room,
    get_room_data_api,
    add_inclusion,
    add_appliance,
    get_all_inclusions,
    get_all_appliances,
    get_room_features,
    manage_features,
    add_inclusion_management,
    edit_inclusion,
    delete_inclusion,
    add_appliance_management,
    edit_appliance,
    delete_appliance,
)

# Import from billing_views
from .billing_views import (
    billing_list,
    generate_bill,
    edit_bill,
    view_bill,
    delete_bill,
    record_payment,
    generate_payment_receipt,
    download_payment_receipt,
    send_payment_receipt,
    delete_payment,
    mark_as_sent,
    upload_payment_proof,
)

# Import from maintenance_views
from .maintenance_views import (
    maintenance_list,
    create_maintenance,
    update_maintenance_status,
    delete_maintenance,
    violation_list,
    create_violation,
    delete_violation,
)

# Import from reminder_views
from .reminder_views import (
    reminder_list,
    create_reminder,
    view_reminder,
    delete_reminder,
    send_reminder_now,
    notification_list,
    mark_notification_read,
    mark_all_notifications_read,
)

# Import helpers
from .helpers import (
    parse_phone,
    get_available_rooms,
    get_dashboard_context,
)

__all__ = [
    # Auth views
    'login_view',
    'signup_view',
    'logout_view',
    'edit_profile',
    'CustomPasswordResetView',
    'custom_password_reset_confirm',
    # Admin views
    'admin_dashboard',
    'admin_list',
    'register_admin',
    'toggle_admin_status',
    'delete_admin',
    # Tenant views
    'tenant_dashboard',
    'tenant_bills',
    'tenant_reports',
    'tenant_submit_maintenance',
    'tenant_submit_violation',
    'tenant_list',
    'add_tenant',
    'edit_tenant',
    'delete_tenant',
    # Room views
    'room_list',
    'tenant_show_rooms',
    'add_room',
    'edit_room',
    'delete_room',
    'get_room_data_api',
    'add_inclusion',
    'add_appliance',
    'get_all_inclusions',
    'get_all_appliances',
    'get_room_features',
    'manage_features',
    'add_inclusion_management',
    'edit_inclusion',
    'delete_inclusion',
    'add_appliance_management',
    'edit_appliance',
    'delete_appliance',
    # Billing views
    'billing_list',
    'generate_bill',
    'edit_bill',
    'view_bill',
    'delete_bill',
    'record_payment',
    'generate_payment_receipt',
    'download_payment_receipt',
    'send_payment_receipt',
    'delete_payment',
    'mark_as_sent',
    # Maintenance views
    'maintenance_list',
    'create_maintenance',
    'update_maintenance_status',
    'delete_maintenance',
    'violation_list',
    'create_violation',
    'delete_violation',
    # Reminder views
    'reminder_list',
    'create_reminder',
    'view_reminder',
    'delete_reminder',
    'send_reminder_now',
    'notification_list',
    'mark_notification_read',
    'mark_all_notifications_read',
    # Helpers
    'parse_phone',
    'get_available_rooms',
    'get_dashboard_context',
]
