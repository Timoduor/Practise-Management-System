from django.contrib import admin
from hub.models.sales import Sales

@admin.register(Sales)
class SalesAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Sales Info", {"fields": ["sales_name", "sales_description", "project_value", "expected_order_date", "sales_status"]}),
        ("Customer", {"fields": ["customer"]}),
        ("Project Manager", {"fields": ["project_manager"]}),
        ("Created By", {"fields": ["created_by"]}),
        ("Organization", {"fields": ["entity", "unit"]}),
    ]
    list_display = ('sales_name', 'customer', 'project_value', 'expected_order_date', 'sales_status', 'project_manager', 'created_by', 'entity', 'unit', 'created_at', 'updated_at')
    search_fields = ('sales_name', 'customer__customer_name', 'project_manager__email')
    list_filter = ('sales_status', 'expected_order_date', 'entity', 'unit', 'is_deleted')
