from django.contrib import admin
from hub.models.contact import Contact

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Contact Info", {"fields": ["contact_name", "contact_email", "contact_phone", "contact_address"]}),
        ("Associated Customer", {"fields": ["customer"]}),
        ("Role", {"fields": ["role"]}),
    ]
    list_display = ('contact_name', 'contact_email', 'contact_phone', 'contact_role', 'customer', 'created_at', 'updated_at')
    search_fields = ('contact_name', 'contact_email', 'contact_role')
    list_filter = ('customer', 'contact_role', 'is_deleted')
