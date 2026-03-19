from django.contrib import admin
from django.utils.html import format_html
from core.models.admin import Admin
from .base_admin import SoftDeleteAdmin

@admin.register(Admin)
class AdminAdmin(SoftDeleteAdmin):
    list_display = (
        'user',
        'admin_type',
        'get_jurisdiction',
        'is_active',
        'created_at',
    )

    search_fields = (
        'user__email',
        'user__firstName',
        'user__surname',
        'admin_type__name',
    )

    list_filter = (
        'is_deleted',
        'admin_type',
        'jurisdiction_content_type',
        'created_at',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
        'created_by',
        'last_updated_by',
    )

    def get_jurisdiction(self, obj):
        """Display jurisdiction information"""
        if obj.jurisdiction_content_type and obj.jurisdiction_object_id:
            content_type = obj.jurisdiction_content_type.model.title()
            try:
                jurisdiction_obj = obj.jurisdiction
                return format_html(
                    '<span title="{}: {}">{} ({})</span>',
                    content_type,
                    jurisdiction_obj,
                    content_type,
                    obj.jurisdiction_object_id
                )
            except Exception:
                return f"{content_type} ({obj.jurisdiction_object_id})"
        return "Global Admin"
    get_jurisdiction.short_description = 'Jurisdiction'
    get_jurisdiction.admin_order_field = 'jurisdiction_content_type'

    def is_active(self, obj):
        """Display active status with color indicator"""
        if not obj.is_deleted:
            return format_html(
                '<span style="color: green;">●</span> Active'
            )
        return format_html(
            '<span style="color: red;">●</span> Inactive'
        )
    is_active.short_description = 'Status'
    is_active.admin_order_field = 'is_deleted'

    fieldsets = (
        ('Admin Information', {
            'fields': (
                'user',
                'admin_type',
            )
        }),
        ('Jurisdiction', {
            'fields': (
                'jurisdiction_content_type',
                'jurisdiction_object_id',
            ),
            'description': 'Specify the scope of administrative control'
        }),
        ('Status Information', {
            'fields': (
                'is_deleted',
                'created_at',
                'created_by',
                'updated_at',
                'last_updated_by',
            ),
            'classes': ('collapse',)
        }),
    )

    class Media:
        css = {
            'all': ('admin/css/admin_admin.css',)
        }