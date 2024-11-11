from django.contrib import admin
from core.models.entity_type import EntityType
from .base_admin import SoftDeleteAdmin



# Register Unit model with custom admin configuration
@admin.register(EntityType)
class EntityType(SoftDeleteAdmin):
    list_display = ('name', 'entity_type' 'description')  # Fields in list view
    search_fields = ('name', 'entity_type')  # Searchable fields
    list_filter = ('entity_type', 'description')  # Filters in the sidebar
