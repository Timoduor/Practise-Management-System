from django.contrib import  admin
from django.contrib.contenttypes.admin import GenericTabularInline
from core.models.admin import Admin

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