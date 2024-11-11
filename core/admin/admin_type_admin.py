from django.contrib import admin
from core.models.admin_type import AdminType
from .base_admin import SoftDeleteAdmin

# Register AdminType model with custom admin configuration
@admin.register(AdminType)
class AdminTypeAdmin(SoftDeleteAdmin):
    list_display = ('name', 'description')  # Fields in list view
    search_fields = ('name',)  # Searchable field for admin type name
