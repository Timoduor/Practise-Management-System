from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from core.models.unit import Unit
from .base_admin import SoftDeleteAdmin, JurisdictionInline

@admin.register(Unit)
class UnitAdmin(SoftDeleteAdmin):
    list_display = (
        'get_unit_name',
        'get_unit_type',
        'get_entity',
        'get_address',
        'is_active',
        'created_at',
    )

    search_fields = (
        'name',
        'address',
        'unit_type__name',
        'entity__entityName',
    )

    list_filter = (
        'is_deleted',
        'unit_type',
        'entity',
        'created_at',
    )

    autocomplete_fields = [
        'unit_type',
        'entity',
    ]

    readonly_fields = (
        'created_at',
        'updated_at',
        'created_by',
        'last_updated_by',
    )

    fieldsets = (
        ('Unit Information', {
            'fields': (
                'name',
                'unit_type',
                'entity',
            )
        }),
        ('Location', {
            'fields': (
                'address',
            ),
            'classes': ('collapse',)
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

    inlines = [JurisdictionInline]

    def get_unit_name(self, obj):
        """Display unit name with status indicator"""
        status_icon = '🔴' if obj.is_deleted else '🟢'
        return format_html(
            '{} <strong>{}</strong>',
            status_icon,
            obj.name
        )
    get_unit_name.short_description = 'Unit Name'
    get_unit_name.admin_order_field = 'name'

    def get_unit_type(self, obj):
        """Display unit type with custom formatting"""
        if obj.unit_type:
            return format_html(
                '<span class="unit-type-tag">{}</span>',
                obj.unit_type
            )
        return '-'
    get_unit_type.short_description = 'Type'
    get_unit_type.admin_order_field = 'unit_type__name'

    def get_entity(self, obj):
        """Display entity with custom formatting"""
        if obj.entity:
            return format_html(
                '<span class="entity-link">{}</span>',
                obj.entity.entityName
            )
        return '-'
    get_entity.short_description = 'Entity'
    get_entity.admin_order_field = 'entity__entityName'

    def get_address(self, obj):
        """Display address with truncation"""
        if obj.address:
            return format_html(
                '<span title="{}">{}</span>',
                obj.address,
                obj.address[:50] + '...' if len(obj.address) > 50 else obj.address
            )
        return '-'
    get_address.short_description = 'Address'
    get_address.admin_order_field = 'address'

    def get_queryset(self, request):
        """Optimize queryset with related fields"""
        return super().get_queryset(request).select_related(
            'unit_type',
            'entity'
        )

    def save_model(self, request, obj, form, change):
        """Track who created/updated the unit"""
        if not change:
            obj.created_by = request.user
        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)

    class Media:
        css = {
            'all': ('admin/css/unit_admin.css',)
        }
        js = ('admin/js/unit_admin.js',)