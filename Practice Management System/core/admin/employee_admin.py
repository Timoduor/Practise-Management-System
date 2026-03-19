from django.contrib import admin
from core.models.employee import Employee
from .base_admin import SoftDeleteAdmin
from django.utils.html import format_html

@admin.register(Employee)
class EmployeeAdmin(SoftDeleteAdmin):
    list_display = (
        'get_employee_name',
        'get_instance',
        'get_entity',
        'get_unit',
        'is_active',
        'created_at',
    )

    search_fields = (
        'user__email',
        'user__firstName',
        'user__surname',
        'instance__name',
        'entity__entityName',
        'unit__name',
    )

    list_filter = (
        'is_deleted',
        'instance',
        'entity',
        'unit',
        'created_at',
    )

    autocomplete_fields = ['user', 'instance', 'entity', 'unit']

    readonly_fields = (
        'created_at',
        'updated_at',
        'created_by',
        'last_updated_by',
    )

    fieldsets = (
        ('Employee Information', {
            'fields': (
                'user',
            )
        }),
        ('Organization Structure', {
            'fields': (
                'instance',
                'entity',
                'unit',
            ),
            'description': 'Assign the employee to their organizational units'
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

    def get_employee_name(self, obj):
        """Display employee name with email"""
        if obj.user:
            return format_html(
                '<strong>{} {}</strong><br><small>{}</small>',
                obj.user.firstName,
                obj.user.surname,
                obj.user.email
            )
        return "No user assigned"
    get_employee_name.short_description = 'Employee'
    get_employee_name.admin_order_field = 'user__firstName'

    def get_instance(self, obj):
        """Display instance with custom formatting"""
        if obj.instance:
            return format_html(
                '<span style="color: #666;">{}</span>',
                obj.instance.name
            )
        return "-"
    get_instance.short_description = 'Instance'
    get_instance.admin_order_field = 'instance__name'

    def get_entity(self, obj):
        """Display entity with custom formatting"""
        if obj.entity:
            return format_html(
                '<span style="color: #666;">{}</span>',
                obj.entity.entityName
            )
        return "-"
    get_entity.short_description = 'Entity'
    get_entity.admin_order_field = 'entity__entityName'

    def get_unit(self, obj):
        """Display unit with custom formatting"""
        if obj.unit:
            return format_html(
                '<span style="color: #666;">{}</span>',
                obj.unit.name
            )
        return "-"
    get_unit.short_description = 'Unit'
    get_unit.admin_order_field = 'unit__name'

    def save_model(self, request, obj, form, change):
        """Track who created/updated the employee"""
        if not change:
            obj.created_by = request.user
        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)

    class Media:
        css = {
            'all': ('admin/css/employee_admin.css',)
        }
        js = ('admin/js/employee_admin.js',)
