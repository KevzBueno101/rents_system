"""
Django admin configuration for dynamic notification system

Provides admin interfaces for managing notification types, templates,
and user preferences.
"""

from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect

from .models import (
    NotificationType,
    NotificationTemplate,
    UserNotificationPreference,
)
from accounts.models import Notification


@admin.register(NotificationType)
class NotificationTypeAdmin(admin.ModelAdmin):
    """Admin interface for notification types"""
    
    list_display = [
        'code', 
        'label', 
        'is_active', 
        'notification_count',
        'template_count',
        'created_at'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['code', 'label', 'description']
    readonly_fields = ['created_at', 'notification_count', 'template_count']
    prepopulated_fields = {'code': ('label',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'label', 'description', 'is_active')
        }),
        ('Appearance', {
            'fields': ('icon', 'color'),
            'description': 'Configure how notifications of this type appear to users.'
        }),
        ('Statistics', {
            'fields': ('notification_count', 'template_count', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def notification_count(self, obj):
        """Count of notifications using this type"""
        count = obj.notifications.count()
        if count > 0:
            url = reverse('admin:accounts_notification_changelist') + f'?dynamic_type__id__exact={obj.id}'
            return format_html('<a href="{}">{}</a>', url, count)
        return count
    notification_count.short_description = 'Notifications'
    
    def template_count(self, obj):
        """Count of templates for this type"""
        return obj.templates.count()
    template_count.short_description = 'Templates'


class NotificationTemplateInline(admin.TabularInline):
    """Inline template editor for notification types"""
    
    model = NotificationTemplate
    extra = 1
    fields = [
        'language', 
        'title_template', 
        'body_template', 
        'is_default',
        'updated_at'
    ]
    readonly_fields = ['updated_at']


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    """Admin interface for notification templates"""
    
    list_display = [
        'notification_type',
        'language',
        'is_default',
        'updated_at'
    ]
    list_filter = ['language', 'is_default', 'notification_type']
    search_fields = ['notification_type__label', 'title_template', 'body_template']
    readonly_fields = ['updated_at']
    
    fieldsets = (
        ('Template Information', {
            'fields': ('notification_type', 'language', 'is_default')
        }),
        ('Template Content', {
            'fields': (
                'title_template',
                'body_template'
            ),
            'description': 'Use {{ variable_name }} for template substitution. Available variables depend on the notification context.'
        }),
        ('Metadata', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['send_test_notification']
    
    def send_test_notification(self, request, queryset):
        """Send test notification to current admin user"""
        from .services import DynamicNotificationService
        
        sent_count = 0
        for template in queryset:
            try:
                DynamicNotificationService.create(
                    user=request.user,
                    type_code=template.notification_type.code,
                    context={
                        'title': 'Test Notification',
                        'message': f'This is a test notification for template: {template.notification_type.label}',
                        'test': True
                    }
                )
                sent_count += 1
            except Exception as e:
                self.message_user(request, f'Error sending test for {template.notification_type.label}: {str(e)}', level='error')
        
        if sent_count > 0:
            self.message_user(request, f'Sent {sent_count} test notification(s) to you.')
    
    send_test_notification.short_description = 'Send test notification to me'


@admin.register(UserNotificationPreference)
class UserNotificationPreferenceAdmin(admin.ModelAdmin):
    """Admin interface for user notification preferences"""
    
    list_display = [
        'user',
        'default_channel',
        'quiet_hours',
        'updated_at'
    ]
    list_filter = ['default_channel', 'updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Default Settings', {
            'fields': ('default_channel',),
            'description': 'Default delivery channel for all notifications.'
        }),
        ('Quiet Hours', {
            'fields': ('quiet_hours_start', 'quiet_hours_end'),
            'description': 'Time period when user should not receive notifications.'
        }),
        ('Type Overrides', {
            'fields': ('type_overrides',),
            'description': 'Per-type channel overrides. Format: {"payment": "email", "reminder": "sms"}'
        }),
        ('Metadata', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
    
    def quiet_hours(self, obj):
        """Display quiet hours in readable format"""
        if obj.quiet_hours_start and obj.quiet_hours_end:
            return f"{obj.quiet_hours_start} - {obj.quiet_hours_end}"
        return "None"
    quiet_hours.short_description = 'Quiet Hours'


# Extend existing Notification admin with bulk actions
class NotificationAdmin(admin.ModelAdmin):
    """Enhanced admin interface for notifications"""
    
    list_display = [
        'user',
        'title',
        'type',
        'is_read',
        'created_at'
    ]
    list_filter = [
        'is_read',
        'type',
        'created_at'
    ]
    search_fields = [
        'user__username',
        'title',
        'message'
    ]
    readonly_fields = [
        'created_at',
    ]
    
    actions = [
        'mark_selected_read',
        'mark_selected_unread',
        'delete_selected_by_type',
        'resend_selected'
    ]
    
    fieldsets = (
        ('Notification Content', {
            'fields': ('user', 'title', 'message', 'link')
        }),
        ('Type', {
            'fields': ('type',)
        }),
        ('Status', {
            'fields': ('is_read',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
        
    def mark_selected_read(self, request, queryset):
        """Mark selected notifications as read"""
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} notification(s) marked as read.")
    
    mark_selected_read.short_description = 'Mark selected as read'
    
    def mark_selected_unread(self, request, queryset):
        """Mark selected notifications as unread"""
        updated = queryset.update(is_read=False)
        self.message_user(request, f"{updated} notification(s) marked as unread.")
    
    mark_selected_unread.short_description = 'Mark selected as unread'
    
    def delete_selected_by_type(self, request, queryset):
        """Delete all notifications of selected types"""
        type_codes = list(set(queryset.values_list('type', flat=True)))
        
        if not type_codes:
            self.message_user(request, "No notification types selected.", level='warning')
            return
        
        from .models import Notification
        deleted_count, _ = Notification.objects.filter(
            user=request.user,
            type__in=type_codes
        ).delete()
        
        self.message_user(request, f"Deleted {deleted_count} notifications of types: {', '.join(type_codes)}")
    
    delete_selected_by_type.short_description = 'Delete all notifications of selected types'
    
    def resend_selected(self, request, queryset):
        """Resend selected notifications"""
        from .services import DynamicNotificationService
        
        resent_count = 0
        for notification in queryset:
            try:
                DynamicNotificationService.create(
                    user=notification.user,
                    type_code=notification.type,
                    context=notification.context_data or {'message': notification.message},
                    link=notification.link,
                    delivery_channel=notification.delivery_channel
                )
                resent_count += 1
            except Exception as e:
                self.message_user(request, f'Error resending notification {notification.id}: {str(e)}', level='error')
        
        if resent_count > 0:
            self.message_user(request, f'Resent {resent_count} notification(s).')
    
    resend_selected.short_description = 'Resend selected notifications'


# Register the enhanced Notification admin
# Note: This will replace any existing Notification admin registration
try:
    admin.site.unregister(Notification)
except admin.sites.NotRegistered:
    pass
admin.site.register(Notification, NotificationAdmin)
