from django.contrib import admin
from .models import *

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Customer Info", {"fields": ["customer_name", "customer_email", "customer_phone", "customer_address"]}),
        ("Organization", {"fields": ["entity", "unit"]}),
    ]
    list_display = ('customer_name', 'customer_email', 'customer_phone', 'entity', 'unit', 'created_at', 'updated_at')
    search_fields = ('customer_name', 'customer_email', 'customer_phone')
    list_filter = ('entity', 'unit', 'is_deleted')

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Contact Info", {"fields": ["contact_name", "contact_email", "contact_phone", "contact_address"]}),
        ("Associated Customer", {"fields": ["customer"]}),
        ("Role", {"fields": ["role"]}),
    ]
    list_display = ('contact_name', 'contact_email', 'contact_phone', 'role', 'customer', 'created_at', 'updated_at')
    search_fields = ('contact_name', 'contact_email', 'role')
    list_filter = ('customer', 'role', 'is_deleted')

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

@admin.register(Sales)
class SalesAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Sales Info", {"fields": ["sales_description", "project_value", "expected_order_date", "sales_status"]}),
        ("Customer", {"fields": ["customer"]}),
        ("Project Manager", {"fields": ["project_manager"]}),
        ("Created By", {"fields": ["created_by"]}),
        ("Organization", {"fields": ["entity", "unit"]}),
    ]
    list_display = ('sales_id', 'customer', 'project_value', 'expected_order_date', 'sales_status', 'project_manager', 'entity', 'unit', 'created_at', 'updated_at')
    search_fields = ('sales_description', 'customer__customer_name', 'project_manager__email')
    list_filter = ('sales_status', 'expected_order_date', 'entity', 'unit', 'is_deleted')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Invoice Info", {"fields": ["invoice_amount", "invoice_date", "paid_status"]}),
        ("Customer", {"fields": ["customer"]}),
        ("Project", {"fields": ["project"]}),
        ("Organization", {"fields": ["entity", "unit"]}),
    ]
    list_display = ('invoice_id', 'customer', 'invoice_amount', 'invoice_date', 'paid_status', 'project', 'entity', 'unit', 'created_at', 'updated_at')
    search_fields = ('invoice_id', 'customer__customer_name', 'project__project_name')
    list_filter = ('paid_status', 'invoice_date', 'entity', 'unit', 'is_deleted')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Task Info", {"fields": ["task_name", "task_description", "action_type", "start_date", "due_date", "task_status"]}),
        ("Project", {"fields": ["project"]}),
        ("Assigned To", {"fields": ["assigned_to"]}),
        ("Organization", {"fields": ["entity", "unit"]}),
    ]
    list_display = ('task_id', 'task_name', 'get_project_name', 'assigned_to', 'start_date', 'due_date', 'task_status', 'entity', 'unit', 'created_at', 'updated_at')
    search_fields = ('task_name', 'project__project_name', 'assigned_to__email')
    list_filter = ('task_status', 'start_date', 'due_date', 'entity', 'unit', 'is_deleted')

    def get_project_name(self, obj):
        return obj.project.project_name
    get_project_name.short_description = 'Project Name'

