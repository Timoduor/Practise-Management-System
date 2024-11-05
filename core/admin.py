# Import necessary modules for Django admin registration and content type handling
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import User, Instance, Entity, Unit, Employee, Admin, AdminType

# Define an abstract admin class for models with soft delete functionality
class SoftDeleteAdmin(admin.ModelAdmin):
    list_filter = ('is_deleted',)  # Filter by deleted status in the admin interface
    readonly_fields = ('created_at', 'updated_at')  # Make timestamp fields read-only

    def get_queryset(self, request):
        # Override default queryset to include all objects, even soft-deleted ones
        return self.model.all_objects.all()

    def delete_model(self, request, obj):
        # Override delete to perform a soft delete
        obj.delete()

    def delete_queryset(self, request, queryset):
        # Override bulk delete to perform a soft delete on each object
        for obj in queryset:
            obj.delete()

# Inline admin for Admin model with Generic ForeignKey (jurisdiction field)
class JurisdictionInline(GenericTabularInline):
    model = Admin  # Inline model is Admin
    extras = 1  # Default to one extra form in the inline

# Register Instance model with custom admin configuration
@admin.register(Instance)
class InstanceAdmin(SoftDeleteAdmin):
    list_display = ('name', 'code', 'industry')  # Fields displayed in the list view
    search_fields = ('name', 'industry')  # Searchable fields in the admin
    # inlines = [JurisdictionInline]  # Uncomment to display jurisdiction inline if needed

# Register Entity model with custom admin configuration
@admin.register(Entity)
class EntityAdmin(SoftDeleteAdmin):
    list_display = ('name', 'entity_type', 'description', 'instance')  # Fields in list view
    search_fields = ('name', 'entity_type')  # Searchable fields in the admin
    list_filter = ('entity_type', 'instance')  # Filters in the sidebar
    # inlines = [JurisdictionInline]  # Uncomment to display jurisdiction inline if needed

# Register Unit model with custom admin configuration
@admin.register(Unit)
class UnitAdmin(SoftDeleteAdmin):
    list_display = ('name', 'unit_type', 'entity')  # Fields in list view
    search_fields = ('name', 'unit_type')  # Searchable fields
    list_filter = ('unit_type', 'entity')  # Filters in the sidebar

# Register User model with custom admin configuration
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number')  # Fields in list view
    search_fields = ('first_name', 'last_name', 'email')  # Searchable fields
    list_filter = ('is_staff', 'is_superuser')  # Filters in the sidebar for staff and superuser
    readonly_fields = ('last_login', 'date_joined')  # Make login timestamps read-only

# Register Employee model with custom admin configuration
@admin.register(Employee)
class EmployeeAdmin(SoftDeleteAdmin):
    list_display = ('user', 'instance', 'entity', 'unit')  # Fields in list view
    search_fields = ('user__first_name', 'user__last_name', 'instance__name', 'entity__name', 'unit__name')  # Searchable fields including related models
    list_filter = ('instance', 'entity', 'unit')  # Filters for instance, entity, and unit

# Register AdminType model with custom admin configuration
@admin.register(AdminType)
class AdminTypeAdmin(SoftDeleteAdmin):
    list_display = ('name', 'description')  # Fields in list view
    search_fields = ('name',)  # Searchable field for admin type name

# Register Admin model with custom admin configuration
@admin.register(Admin)
class AdminAdmin(SoftDeleteAdmin):
    list_display = ('user', 'admin_type', 'jurisdiction_content_type', 'jurisdiction_object_id')  # Fields in list view
    search_fields = ('user__first_name', 'user__last_name', 'admin_type__name')  # Searchable fields
    list_filter = ('admin_type', 'jurisdiction_content_type')  # Filters for admin type and jurisdiction content type
