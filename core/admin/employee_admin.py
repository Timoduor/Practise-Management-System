from core.models.employee import Employee
from django.contrib import admin
from .base_admin import SoftDeleteAdmin

# Register Employee model with custom admin configuration
@admin.register(Employee)
class EmployeeAdmin(SoftDeleteAdmin):
    list_display = ('user', 'instance', 'entity', 'unit')  # Fields in list view
    search_fields = ('user__first_name', 'user__last_name', 'instance__name', 'entity__name', 'unit__name')  # Searchable fields including related models
    list_filter = ('instance', 'entity', 'unit')  # Filters for instance, entity, and unit

