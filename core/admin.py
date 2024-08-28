from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import User, Instance, Entity, Unit, Employee, Admin, AdminType

# Register the SoftDeleteModel abstract class so that it's reflected in the admin

class SoftDeleteAdmin(admin.ModelAdmin):
    list_filter = ('is_deleted',)
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        return self.model.all_objects.all()

    def delete_model(self, request, obj):
        obj.delete()

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()

# Inline Admin for Generic ForeignKey (Admin jurisdiction)
class JurisdictionInline(GenericTabularInline):
    model = Admin
    extras = 1

@admin.register(Instance)
class InstanceAdmin(SoftDeleteAdmin):
    list_display = ('name', 'code', 'industry')
    search_fields = ('name', 'industry')
    # inlines = [JurisdictionInline]

@admin.register(Entity)
class EntityAdmin(SoftDeleteAdmin):
    list_display = ('name', 'entity_type', 'description', 'instance')
    search_fields = ('name', 'entity_type')
    list_filter = ('entity_type', 'instance')
    # inlines = [JurisdictionInline]

@admin.register(Unit)
class UnitAdmin(SoftDeleteAdmin):
    list_display = ('name', 'unit_type', 'entity')
    search_fields = ('name', 'unit_type')
    list_filter = ('unit_type', 'entity')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('is_staff', 'is_superuser')
    readonly_fields = ('last_login', 'date_joined')

@admin.register(Employee)
class EmployeeAdmin(SoftDeleteAdmin):
    list_display = ('user', 'instance', 'entity', 'unit')
    search_fields = ('user__first_name', 'user__last_name', 'instance__name', 'entity__name', 'unit__name')
    list_filter = ('instance', 'entity', 'unit')

@admin.register(AdminType)
class AdminTypeAdmin(SoftDeleteAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Admin)
class AdminAdmin(SoftDeleteAdmin):
    list_display = ('user', 'admin_type', 'jurisdiction_content_type', 'jurisdiction_object_id')
    search_fields = ('user__first_name', 'user__last_name', 'admin_type__name')
    list_filter = ('admin_type', 'jurisdiction_content_type')
