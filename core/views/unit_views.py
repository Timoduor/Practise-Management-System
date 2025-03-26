from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from core.models.unit import Unit
from core.serializers.unit_serializers import UnitSerializer
from core.permissions import ReadOnlyUnlessSuperadmin

class UnitViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Units:
    - All authenticated users can read (GET) all units.
    - Only superadmins can create/update/delete units.
    """
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [IsAuthenticated, ReadOnlyUnlessSuperadmin]

    def get_queryset(self):
        """
        Returns all units for all authenticated users.
        """
        user = self.request.user
        # If the user is authenticated, return all Units
        if user.is_authenticated:
            return Unit.objects.all()

        return Unit.objects.none()
