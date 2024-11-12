from django.contrib import admin
from hub.models.invoice import Invoice

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
