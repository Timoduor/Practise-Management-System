from django.contrib import admin
from core.models.unit_type import UnitType
from .base_admin import SoftDeleteAdmin



# Register Unit model with custom admin configuration
@admin.register(UnitType)
class UnitType(SoftDeleteAdmin):
    list_display = ('name', 'unit_type' 'description')  # Fields in list view
    search_fields = ('name', 'unit_type')  # Searchable fields
    list_filter = ('unit_type', 'description')  # Filters in the sidebar
