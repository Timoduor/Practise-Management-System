from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from core.models.unit_type import UnitType
from .base_admin import SoftDeleteAdmin

@admin.register(UnitType)
class UnitTypeAdmin(SoftDeleteAdmin):
    list_display = (
        'get_name',
        'get_description',
        'get_units_count',
        'is_active',
        'created_at',
    )

    search_fields = (
        'name',
        'description',
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

    fieldsets = (
        ('Unit Type Information', {
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

    def get_name(self, obj):
        """Display unit type name with status indicator"""
        status_icon = '🔴' if obj.is_deleted else '🟢'
        return format_html(
            '{} <strong>{}</strong>',
            status_icon,
            obj.name
        )
    get_name.short_description = 'Name'
    get_name.admin_order_field = 'name'

    def get_description(self, obj):
        """Display description with truncation"""
        if obj.description:
            return format_html(
                '<span title="{}">{}</span>',
                obj.description,
                obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
            )
        return '-'
    get_description.short_description = 'Description'
    get_description.admin_order_field = 'description'

    def get_units_count(self, obj):
        """Display count of units using this type"""
        count = obj.unit_set.count()
        return format_html(
            '<span class="unit-count">{}</span>',
            count
        )
    get_units_count.short_description = 'Units'
    get_units_count.admin_order_field = 'unit_count'

    def get_queryset(self, request):
        """Optimize queryset with annotations"""
        return super().get_queryset(request).annotate(
            unit_count=models.Count('unit')
        )

    def save_model(self, request, obj, form, change):
        """Track who created/updated the unit type"""
        if not change:
            obj.created_by = request.user
        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)

    class Media:
        css = {
            'all': (
                'admin/css/unit_type_admin.css',
            )
        }
        js = (
            'admin/js/unit_type_admin.js',
        )