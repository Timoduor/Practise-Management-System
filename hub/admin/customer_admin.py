from django.contrib import admin
from hub.models.customer import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Customer Info", {"fields": ["customer_name", "customer_email", "customer_phone", "customer_address"]}),
        ("Organization", {"fields": ["entity", "unit"]}),
    ]
    list_display = ('customer_name', 'customer_email', 'customer_phone', 'entity', 'unit', 'created_at', 'updated_at')
    search_fields = ('customer_name', 'customer_email', 'customer_phone')
    list_filter = ('entity', 'unit', 'is_deleted')
