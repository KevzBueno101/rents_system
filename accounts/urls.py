from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views
from .views import admin_views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    
    # ─── PASSWORD RESET ──────────────────────────────
    path('password-reset/',
         views.CustomPasswordResetView.as_view(),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html',
         ),
         name='password_reset_done'),

    path('password-reset/confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
         ),
         name='password_reset_confirm'),

    path('password-reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html',
         ),
         name='password_reset_complete'),
    
    # ─── ADMIN ───────────────────────────────────────
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('audit-trail/', admin_views.audit_trail, name='audit_trail'),
    path('admin-list/', views.admin_list, name='admin_list'),
    path('register-admin/', views.register_admin, name='register_admin'),
    path('toggle-admin/<int:user_id>/', views.toggle_admin_status, name='toggle_admin_status'),
    path('delete-admin/<int:user_id>/', views.delete_admin, name='delete_admin'),

    # ─── TENANTS ─────────────────────────────────────
    path('tenant-dashboard/', views.tenant_dashboard, name='tenant_dashboard'),
    path('tenant-list/', views.tenant_list, name='tenant_list'),
    path('add-tenant/', views.add_tenant, name='add_tenant'),
    path('edit-tenant/<int:tenant_id>/', views.edit_tenant, name='edit_tenant'),
    path('delete-tenant/<int:tenant_id>/', views.delete_tenant, name='delete_tenant'),

    # ─── AUTH ─────────────────────────────────────────
    path('logout/', views.logout_view, name='logout'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),

    # ─── ROOMS ───────────────────────────────────────
    path('room-list/', views.room_list, name='room_list'),
    path('add-room/', views.add_room, name='add_room'),
    path('edit-room/<int:room_id>/', views.edit_room, name='edit_room'),
    path('delete-room/<int:room_id>/', views.delete_room, name='delete_room'),
    path('api/room-data/<int:room_id>/', views.get_room_data_api, name='get_room_data_api'),
    
    # ─── ROOM FEATURES ─────────────────────────────
    path('add-inclusion/', views.add_inclusion, name='add_inclusion'),
    path('add-appliance/', views.add_appliance, name='add_appliance'),
    path('get-all-inclusions/', views.get_all_inclusions, name='get_all_inclusions'),
    path('get-all-appliances/', views.get_all_appliances, name='get_all_appliances'),
    path('get-room-features/', views.get_room_features, name='get_room_features'),
    
    # ─── FEATURE MANAGEMENT ─────────────────────────
    path('manage-features/', views.manage_features, name='manage_features'),
    path('add-inclusion-management/', views.add_inclusion_management, name='add_inclusion_management'),
    path('edit-inclusion/<int:inclusion_id>/', views.edit_inclusion, name='edit_inclusion'),
    path('delete-inclusion/<int:inclusion_id>/', views.delete_inclusion, name='delete_inclusion'),
    path('add-appliance-management/', views.add_appliance_management, name='add_appliance_management'),
    path('edit-appliance/<int:appliance_id>/', views.edit_appliance, name='edit_appliance'),
    path('delete-appliance/<int:appliance_id>/', views.delete_appliance, name='delete_appliance'),

    # ─── BILLING ─────────────────────────────────────
    path('billing/', views.billing_list, name='billing_list'),
    path('billing/generate/', views.generate_bill, name='generate_bill'),
    path('billing/edit/<int:bill_id>/', views.edit_bill, name='edit_bill'),
    path('billing/view/<int:bill_id>/', views.view_bill, name='view_bill'),
    path('billing/delete/<int:bill_id>/', views.delete_bill, name='delete_bill'),
    path('billing/pay/<int:bill_id>/', views.record_payment, name='record_payment'),
    path('billing/delete-payment/<int:payment_id>/', views.delete_payment, name='delete_payment'),
    path('billing/mark-sent/<int:bill_id>/', views.mark_as_sent, name='mark_as_sent'),

    # ─── REMINDERS ───────────────────────────────────
    path('reminders/', views.reminder_list, name='reminder_list'),
    path('reminders/create/', views.create_reminder, name='create_reminder'),
    path('reminders/view/<int:reminder_id>/', views.view_reminder, name='view_reminder'),
    path('reminders/delete/<int:reminder_id>/', views.delete_reminder, name='delete_reminder'),
    path('reminders/send/<int:reminder_id>/', views.send_reminder_now, name='send_reminder_now'),

    # ─── NOTIFICATIONS ───────────────────────────────
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),

    # ─── MAINTENANCE ─────────────────────────────────
    path('maintenance/', views.maintenance_list, name='maintenance_list'),
    path('maintenance/create/', views.create_maintenance, name='create_maintenance'),
    path('maintenance/update/<int:report_id>/', views.update_maintenance_status, name='update_maintenance_status'),
    path('maintenance/delete/<int:report_id>/', views.delete_maintenance, name='delete_maintenance'),

    # ─── VIOLATIONS ─────────────────────────────────
    path('violations/', views.violation_list, name='violation_list'),
    path('violations/create/', views.create_violation, name='create_violation'),
    path('violations/delete/<int:violation_id>/', views.delete_violation, name='delete_violation'),
]