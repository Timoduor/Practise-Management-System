from django.contrib import admin
from core.models.unit import Unit
from .base_admin import SoftDeleteAdmin



# Register Unit model with custom admin configuration
@admin.register(Unit)
class UnitAdmin(SoftDeleteAdmin):
    list_display = ('name', 'unit_type', 'entity')  # Fields in list view
    search_fields = ('name', 'unit_type')  # Searchable fields
    list_filter = ('unit_type', 'entity')  # Filters in the sidebar
