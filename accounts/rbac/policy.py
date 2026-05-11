"""
Named URL routing policy for RBAC.

Rules are keyed on resolver url_name values for reliable checks across refactor.
"""

SESSION_PORTAL_KEY = '_rents_portal'


PUBLIC_ROUTE_NAMES = frozenset(
    {
        'home',
        'login',
        'signup',
        'admin_login',
        'password_reset',
        'password_reset_done',
        'password_reset_confirm',
        'password_reset_complete',
        'check_username_availability',
    }
)


TENANT_PORTAL_ROUTE_NAMES = frozenset(
    {
        'tenant_dashboard',
        'tenant_dashboard_legacy',
        'tenant_show_rooms',
        'tenant_bills',
        'tenant_billing',
        'tenant_reports',
        'tenant_submit_maintenance',
        'tenant_submit_violation',
        'tenant_rules',
        'notification_list',
        'mark_notification_read',
        'mark_all_notifications_read',
        'mark_notification',
        'api_tenant_dashboard_data',
        'upload_payment_proof',
    }
)


SHARED_AUTH_ROUTE_NAMES = frozenset(
    {
        'logout',
        'edit_profile',
        'download_payment_receipt',
        'get_current_user_info',
        'update_username',
        'api_rules_data',
    }
)


STAFF_PORTAL_ROUTE_NAMES = frozenset(
    {
        'admin_dashboard',
        'audit_trail',
        'admin_list',
        'register_admin',
        'toggle_admin_status',
        'delete_admin',
        'tenant_list',
        'add_tenant',
        'edit_tenant',
        'delete_tenant',
        'room_list',
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
        'billing_list',
        'generate_bill',
        'edit_bill',
        'view_bill',
        'delete_bill',
        'record_payment',
        'generate_payment_receipt',
        'send_payment_receipt',
        'delete_payment',
        'mark_as_sent',
        'reminder_list',
        'create_reminder',
        'view_reminder',
        'delete_reminder',
        'send_reminder_now',
        'maintenance_list',
        'create_maintenance',
        'update_maintenance_status',
        'delete_maintenance',
        'violation_list',
        'create_violation',
        'delete_violation',
        'rules_list',
        'create_rule',
        'edit_rule',
        'delete_rule',
    }
)


def route_sets_are_disjoint():
    dup = TENANT_PORTAL_ROUTE_NAMES & STAFF_PORTAL_ROUTE_NAMES
    if dup:
        raise ValueError(f'TENANT_PORTAL_ROUTE_NAMES overlaps STAFF_PORTAL_ROUTE_NAMES: {dup}')
    return True


route_sets_are_disjoint()
