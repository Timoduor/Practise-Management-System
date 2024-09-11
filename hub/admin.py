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


@admin.register(ProjectPhase)
class ProjectPhaseAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Phase Info", {"fields": ["phase_name", "phase_description", "start_date", "end_date"]}),
        ("Associated Project", {"fields": ["project"]}),
    ]
    list_display = ('phase_name', 'project', 'start_date', 'end_date', 'created_at', 'updated_at')
    search_fields = ('phase_name', 'project__project_name')
    list_filter = ('start_date', 'end_date', 'is_deleted')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Task Info", {"fields": ["task_name", "task_description", "start_date", "due_date", "task_status"]}),
        ("Phase", {"fields": ["phase"]}),
        ("Assigned To", {"fields": ["assigned_to"]}),
    ]
    list_display = ('task_name', 'get_phase_name', 'assigned_to', 'start_date', 'due_date', 'task_status', 'created_at', 'updated_at')
    search_fields = ('task_name', 'phase__phase_name', 'assigned_to__email')
    list_filter = ('task_status', 'start_date', 'due_date', 'is_deleted')

    def get_phase_name(self, obj):
        return obj.phase.phase_name
    get_phase_name.short_description = 'Phase Name'


@admin.register(WorkEntries)
class WorkEntriesAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Work Info", {"fields": ["date", "start_time", "end_time", "description", "task_type"]}),
        ("Task", {"fields": ["project", "phase", "task"]}),
        ("User", {"fields": ["user"]}),
    ]
    list_display = ('user', 'date', 'start_time', 'end_time', 'task_type', 'project', 'phase', 'task', 'created_at', 'updated_at')
    search_fields = ('user__email', 'project__project_name', 'phase__phase_name', 'task__task_name')
    list_filter = ('task_type', 'project', 'phase', 'date', 'is_deleted')


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Leave Info", {"fields": ["name", "description", "is_paid"]}),
    ]
    list_display = ('name', 'description', 'is_paid')
    search_fields = ('name',)
    list_filter = ('is_paid',)


@admin.register(Absence)
class AbsenceAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Absence Info", {"fields": ["absence_date", "start_time", "end_time", "absence_description"]}),
        ("Project", {"fields": ["project"]}),
        ("User", {"fields": ["user", "leave_type"]}),
    ]
    list_display = ('user', 'absence_date', 'start_time', 'end_time', 'project', 'leave_type', 'created_at', 'updated_at')
    search_fields = ('user__email', 'project__project_name', 'leave_type__name')
    list_filter = ('absence_date', 'leave_type', 'project', 'is_deleted')


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Expense Info", {"fields": ["value", "date", "description"]}),
        ("Project Info", {"fields": ["project", "phase", "task"]}),
        ("User", {"fields": ["user"]}),
    ]
    list_display = ('user', 'project', 'phase', 'task', 'value', 'date', 'created_at', 'updated_at')
    search_fields = ('user__email', 'project__project_name', 'phase__phase_name', 'task__task_name')
    list_filter = ('date', 'project', 'phase', 'task', 'is_deleted')


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
