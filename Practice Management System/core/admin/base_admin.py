from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.html import format_html
from django.utils import timezone
from core.models.admin import Admin
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from core.models.admin import Admin

class SoftDeleteAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'is_active',
        'get_created_info',
        'get_updated_info',
    )
    
    list_filter = (
        'is_deleted',
        'created_at',
        'updated_at',
    )
    
    readonly_fields = (
        'created_at',
        'updated_at',
        'created_by',
        'last_updated_by',
    )

    actions = [
        'soft_delete_selected',
        'restore_selected',
        'hard_delete_selected',
    ]

    def get_queryset(self, request):
        """Override to show all objects including soft-deleted ones"""
        return self.model.all_objects.all()

    def is_active(self, obj):
        """Show active status with colored indicator"""
        if not obj.is_deleted:
            return format_html(
                '<span style="color: green;">●</span> Active'
            )
        return format_html(
            '<span style="color: red;">●</span> Deleted'
        )
    is_active.short_description = 'Status'

    def get_created_info(self, obj):
        """Display creation info with user if available"""
        if obj.created_by:
            return format_html(
                '{}<br><small>by {}</small>',
                obj.created_at.strftime('%Y-%m-%d %H:%M'),
                obj.created_by
            )
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    get_created_info.short_description = 'Created'

    def get_updated_info(self, obj):
        """Display last update info with user if available"""
        if obj.last_updated_by:
            return format_html(
                '{}<br><small>by {}</small>',
                obj.updated_at.strftime('%Y-%m-%d %H:%M'),
                obj.last_updated_by
            )
        return obj.updated_at.strftime('%Y-%m-%d %H:%M')
    get_updated_info.short_description = 'Last Updated'

    def save_model(self, request, obj, form, change):
        """Track who created/updated the object"""
        if not change:  # New object
            obj.created_by = request.user
        obj.last_updated_by = request.user
        obj.save()

    def soft_delete_selected(self, request, queryset):
        """Soft delete selected objects"""
        for obj in queryset:
            obj.delete()
        self.message_user(request, f"{queryset.count()} items have been soft deleted.")
    soft_delete_selected.short_description = "Soft delete selected items"

    def restore_selected(self, request, queryset):
        """Restore selected soft-deleted objects"""
        for obj in queryset:
            obj.undelete()
        self.message_user(request, f"{queryset.count()} items have been restored.")
    restore_selected.short_description = "Restore selected items"

    def hard_delete_selected(self, request, queryset):
        """Permanently delete selected objects"""
        count = queryset.count()
        for obj in queryset:
            obj.hard_delete()
        self.message_user(request, f"{count} items have been permanently deleted.")
    hard_delete_selected.short_description = "⚠️ Permanently delete selected items"

    def get_fieldsets(self, request, obj=None):
        """Default fieldsets for models using this admin class"""
        fieldsets = super().get_fieldsets(request, obj)
        if not fieldsets:
            fields = [f.name for f in self.model._meta.fields if f.name not in self.readonly_fields]
            fieldsets = (
                (None, {
                    'fields': fields
                }),
                ('History', {
                    'fields': self.readonly_fields,
                    'classes': ('collapse',)
                }),
            )
        return fieldsets


class JurisdictionInline(GenericTabularInline):
    model = Admin
    extra = 1
    ct_fk_field = "jurisdiction_object_id"
    ct_field = "jurisdiction_content_type"
    fields = ('user', 'admin_type', 'is_deleted')
    readonly_fields = ('created_at', 'updated_at')