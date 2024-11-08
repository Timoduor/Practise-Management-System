from django.contrib import admin
from core.models.user import User


# Register User model with custom admin configuration
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number')  # Fields in list view
    search_fields = ('first_name', 'last_name', 'email')  # Searchable fields
    list_filter = ('is_staff', 'is_superuser')  # Filters in the sidebar for staff and superuser
    readonly_fields = ('last_login', 'date_joined')  # Make login timestamps read-only

