from django.contrib import admin
from hub.models.project import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Project Info", {"fields": ["project_name", "project_description", "start_date", "end_date"]}),
        ("Customer", {"fields": ["customer"]}),
        ("Organization", {"fields": ["entity", "unit"]}),
    ]
    list_display = ('project_name', 'customer', 'start_date', 'end_date', 'entity', 'unit', 'created_at', 'updated_at')
    search_fields = ('project_name', 'customer__customer_name')
    list_filter = ('start_date', 'end_date', 'entity', 'unit', 'is_deleted')
