from django.contrib import admin
from core.models.entity_type import EntityType
from .base_admin import SoftDeleteAdmin



# Register Unit model with custom admin configuration
@admin.register(EntityType)
class EntityTypeAdmin(SoftDeleteAdmin):
    list_display = ('name', 'description')  # Fields in list view
    search_fields = ('name', )  # Searchable fields
    list_filter = ('name', )  # Filters in the sidebar