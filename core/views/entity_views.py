from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from core.models.entity import Entity
from core.serializers.entity_serializers import EntitySerializer
from core.permissions import ReadOnlyUnlessSuperadmin

class EntityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Entities:
    - All authenticated users can read (GET) all entities.
    - Only superadmins can create/update/delete entities.
    """
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer
    permission_classes = [IsAuthenticated, ReadOnlyUnlessSuperadmin]

    def get_queryset(self):
        """
        Returns all entities for all authenticated users.
        """
        user = self.request.user
        # If the user is authenticated, return all Entities
        if user.is_authenticated:
            return Entity.objects.all()

        # If the user isn't authenticated, return none (should be blocked anyway by IsAuthenticated)
        return Entity.objects.none()
