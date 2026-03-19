from django.contrib import admin
from django.utils.html import format_html
from core.models.admin_type import AdminType
from .base_admin import SoftDeleteAdmin

@admin.register(AdminType)
class AdminTypeAdmin(SoftDeleteAdmin):
    list_display = (
        'name',
        'description',
        'created_at',
    )

    search_fields = (
        'name',
        'description',
    )

    list_filter = (
        'is_deleted',
        'created_at',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
        'created_by',
        'last_updated_by',
    )

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name',
                'description',
            )
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