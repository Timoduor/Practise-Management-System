from core.models.entity import Entity
from django.contrib import admin
from .base_admin import SoftDeleteAdmin

# Register Entity model with custom admin configuration
@admin.register(Entity)
class EntityAdmin(SoftDeleteAdmin):
    list_display = ('name', 'entity_type', 'description', 'instance')  # Fields in list view
    search_fields = ('name', 'entity_type')  # Searchable fields in the admin
    list_filter = ('entity_type', 'instance')  # Filters in the sidebar
    # inlines = [JurisdictionInline]  # Uncomment to display jurisdiction inline if needed
