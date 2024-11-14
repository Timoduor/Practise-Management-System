from django.contrib import admin
from core.models.unit_type import UnitType
from .base_admin import SoftDeleteAdmin



# Register Unit model with custom admin configuration
@admin.register(UnitType)
class UnitTypeAdmin(SoftDeleteAdmin):
    list_display = ('name', 'description')  # Fields in list view
    search_fields = ('name', )  # Searchable fields
    list_filter = ('name', )  # Filters in the sidebar
