from django.contrib import admin
from .base_admin import SoftDeleteAdmin
from core.models.instance import Instance


# Register Instance model with custom admin configuration
@admin.register(Instance)
class InstanceAdmin(SoftDeleteAdmin):
    list_display = ('name', 'code', 'industry')  # Fields displayed in the list view
    search_fields = ('name', 'industry')  # Searchable fields in the admin
    # inlines = [JurisdictionInline]  # Uncomment to display jurisdiction inline if needed

