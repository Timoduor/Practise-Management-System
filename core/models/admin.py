from django.db import models
from .base import SoftDeleteModel
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib import admin

from core.models.instance import Instance
from core.models.entity import Entity
from core.models.unit import Unit
from core.models.organisation_role import OrganisationRole
from core.models.permission_profile import PermissionProfile, Permission


class Admin(SoftDeleteModel):
    user = models.OneToOneField("core.User", on_delete=models.CASCADE, related_name="admin_user")
    admin_type = models.ForeignKey("core.AdminType", on_delete=models.SET_NULL, null=True, blank=True)

    # Generic foreign key fields
    jurisdiction_content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, blank=True, null=True)
    jurisdiction_object_id = models.PositiveIntegerField(blank=True, null=True)
    jurisdiction = GenericForeignKey("jurisdiction_content_type", "jurisdiction_object_id")

    # Direct foreign keys for jurisdiction targets
    entity = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL)
    unit = models.ForeignKey(Unit, null=True, blank=True, on_delete=models.SET_NULL)
    instance = models.ForeignKey(Instance, null=True, blank=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        # Auto-assign jurisdiction content type and object ID based on admin_type
        if self.admin_type:
            if self.admin_type.name == "ENT" and self.entity:
                self.jurisdiction_content_type = ContentType.objects.get_for_model(Entity)
                self.jurisdiction_object_id = self.entity.id
            elif self.admin_type.name == "UNI" and self.unit:
                self.jurisdiction_content_type = ContentType.objects.get_for_model(Unit)
                self.jurisdiction_object_id = self.unit.id
            elif self.admin_type.name == "INS" and self.instance:
                self.jurisdiction_content_type = ContentType.objects.get_for_model(Instance)
                self.jurisdiction_object_id = self.instance.id
            else:
                self.jurisdiction_content_type = None
                self.jurisdiction_object_id = None
        else:
            self.jurisdiction_content_type = None
            self.jurisdiction_object_id = None

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Admin: {self.user.username} ({self.admin_type.name if self.admin_type else 'No Type'})"

""""
@admin.register(Admin)
class AdminModelAdmin(admin.ModelAdmin):
    readonly_fields = ('jurisdiction_content_type', 'jurisdiction_object_id', 'jurisdiction_display')
    list_display = ('user', 'admin_type', 'jurisdiction_display')

    def jurisdiction_display(self, obj):
        return str(obj.jurisdiction) if obj.jurisdiction else "None"

    jurisdiction_display.short_description = "Jurisdiction"

"""    


@admin.register(OrganisationRole)
class OrganisationRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'organisation', 'role', 'is_active', 'assigned_at')
    list_filter = ('role', 'is_active', 'organisation')
    search_fields = ('user__username', 'organisation__orgName')


@admin.register(PermissionProfile)
class PermissionProfileAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('profile', 'code')
