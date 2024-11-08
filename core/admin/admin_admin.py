from django.contrib import admin
from .base_admin import SoftDeleteAdmin
from core.models.admin import Admin

#Register Admin model with custom admin configuration
@admin.register(Admin)
class AdminAdmin(SoftDeleteAdmin):
    list_display = ('user', 'admin_type', 'jurisdiction_content_type', 'jurisdiction_object_id')  # Fields in list view
    search_fields = ('user__first_name', 'user__last_name', 'admin_type__name')  # Searchable fields
    list_filter = ('admin_type', 'jurisdiction_content_type') 