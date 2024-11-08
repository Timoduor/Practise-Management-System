from django.db import models

# Define a queryset for models with soft delete functionality
class SoftDeleteQuerySet(models.QuerySet):

    def delete(self):
        # Perform a soft delete by updating `is_deleted` to True
        return super().update(is_deleted=True)

    def hard_delete(self):
        # Permanently delete the record from the database
        return super().delete()

    def undelete(self):
        # Restore a soft-deleted record by setting `is_deleted` to False
        return super().update(is_deleted=False)

# Define a manager for models with soft delete functionality
class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        # Override the default queryset to exclude soft-deleted records
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)

# Define a base model with soft delete functionality and timestamp tracking
class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)  # Field to mark soft deletion status
    created_at = models.DateTimeField(auto_now_add=True)  # Auto-set on record creation
    updated_at = models.DateTimeField(auto_now=True)  # Auto-updated on record update
    last_updated_by = models.ForeignKey("core.User", null=True, blank=True, on_delete=models.DO_NOTHING, related_name='%(class)s_last_updated_by')  # User who last updated
    created_by = models.ForeignKey("core.User", null=True, blank=True, on_delete=models.DO_NOTHING, related_name='%(class)s_created_by')  # User who created

    # Managers for handling soft-deleted records
    objects = SoftDeleteManager()
    all_objects = models.Manager()  # Manager that includes soft-deleted records

    class Meta:
        abstract = True  # Abstract base class, won't create a table

    def delete(self, using=None, keep_parents=False):
        # Override delete method to perform a soft delete
        self.is_deleted = True
        self.save()

    def hard_delete(self):
        # Permanently delete the instance
        super().delete()

    def undelete(self):
        # Restore a soft-deleted instance
        self.is_deleted = False
        self.save()
