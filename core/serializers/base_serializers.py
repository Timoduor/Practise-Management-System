


# Mixin class to enable soft delete functionality in serializers
class SoftDeleteMixin:
    def perform_soft_delete(self, instance):
        # Call the soft delete method defined in the model
        instance.delete()

