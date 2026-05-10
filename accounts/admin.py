from django.contrib import admin
from .models import Rule, Room, RoomImage


class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 3
    fields = ['image', 'order']
    ordering = ['order']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_code', 'floor', 'capacity', 'monthly_rate', 'status', 'image_count']
    list_filter = ['floor', 'bed_type', 'water_included', 'electricity_included', 'has_wifi']
    search_fields = ['room_number', 'room_code']
    readonly_fields = ['room_code', 'occupied_beds', 'available_beds', 'status']
    inlines = [RoomImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('room_number', 'floor', 'capacity', 'monthly_rate', 'photo')
        }),
        ('Room Features', {
            'fields': ('area', 'num_cr', 'bed_type', 'has_lababo')
        }),
        ('Inclusions', {
            'fields': ('water_included', 'electricity_included', 'has_wifi', 'dynamic_inclusions')
        }),
        ('Status Information', {
            'fields': ('room_code', 'occupied_beds', 'available_beds', 'status'),
            'classes': ('collapse',)
        }),
    )
    
    def image_count(self, obj):
        return obj.additional_images.count() + (1 if obj.photo else 0)
    image_count.short_description = 'Images'
    
    def occupied_beds(self, obj):
        return obj.occupied_beds()
    
    def available_beds(self, obj):
        return obj.available_beds()
    
    def status(self, obj):
        return obj.status()


@admin.register(RoomImage)
class RoomImageAdmin(admin.ModelAdmin):
    list_display = ['room', 'order', 'created_at', 'image_preview']
    list_filter = ['room__floor', 'created_at']
    search_fields = ['room__room_number', 'room__room_code']
    ordering = ['room', 'order']
    
    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="50" height="50" style="object-fit: cover;">'
        return 'No image'
    image_preview.allow_tags = True
    image_preview.short_description = 'Preview'


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
