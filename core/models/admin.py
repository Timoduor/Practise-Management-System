from django.db import models
from .base import SoftDeleteModel
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


# Define Admin model to link users with admin roles and permissions
class Admin(SoftDeleteModel):
    user = models.OneToOneField("core.User", on_delete=models.CASCADE, related_name="admin_user")  # Linked user
    admin_type = models.ForeignKey("AdminType", on_delete=models.SET_NULL, null=True, blank=True)  # Admin type

    # Define jurisdiction for admin based on ContentType and object ID
    jurisdiction_content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, blank=True, null=True)
    jurisdiction_object_id = models.PositiveIntegerField(blank=True, null=True)
    jurisdiction = GenericForeignKey("jurisdiction_content_type", "jurisdiction_object_id")

    def save(self, *args, **kwargs):
        # Automatically set the jurisdiction type based on admin_type
        if self.admin_type.name == "ENT":
            self.jurisdiction_content_type = ContentType.objects.get_for_model("Entity")
        elif self.admin_type.name == "UNI":
            self.jurisdiction_content_type = ContentType.objects.get_for_model("Unit")
        elif self.admin_type.name == "INS":
            self.jurisdiction_content_type = ContentType.objects.get_for_model("Instance")
        else:
            self.jurisdiction_content_type = None
            self.jurisdiction_object_id = None
            self.jurisdiction = None
            self.is_superuser = True

        # Save the instance with updated values
        super().save(*args, **kwargs)
