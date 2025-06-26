from django.contrib import admin
from hub.models.customer import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    # autocomplete_fields = ['organisation']  # enables searchable dropdown

    fieldsets = [
        ("organization", {  # ✅ Moved this section to the top
            "fields": ["organisation"]
        }),
        ("Customer Info", {
            "fields": ["customer_name", "customer_email", "customer_phone", "customer_address"]
        }),
        ("Structure Info", {
            "fields": ["instance", "entity", "unit"]
        }),
    ]

    list_display = (
        'customer_name', 'customer_email', 'customer_phone',
        'organisation', 'instance', 'entity', 'unit',
        'created_at', 'updated_at'
    )

    search_fields = ('customer_name', 'customer_email', 'customer_phone')
    list_filter = ('organisation', 'instance', 'entity', 'unit', 'is_deleted')




