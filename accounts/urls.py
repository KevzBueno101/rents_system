from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views

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
]