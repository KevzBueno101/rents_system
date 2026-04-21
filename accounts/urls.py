from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('tenant-dashboard/', views.tenant_dashboard, name='tenant_dashboard'),
    path('register-admin/', views.register_admin, name='register_admin'),
    path('admin-list/', views.admin_list, name='admin_list'),
    path('toggle-admin/<int:user_id>/', views.toggle_admin_status, name='toggle_admin_status'),
    path('delete-admin/<int:user_id>/', views.delete_admin, name='delete_admin'),
    path('tenant-list/', views.tenant_list, name='tenant_list'),
    path('add-tenant/', views.add_tenant, name='add_tenant'),
    path('edit-tenant/<int:tenant_id>/', views.edit_tenant, name='edit_tenant'),
    path('delete-tenant/<int:tenant_id>/', views.delete_tenant, name='delete_tenant'),
    path('logout/', views.logout_view, name='logout'),
]