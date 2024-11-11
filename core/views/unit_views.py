from rest_framework import viewsets
from core.models.unit import Unit
from core.serializers.unit_serializers import UnitSerializer

# Define a viewset for managing Unit objects
class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()  # Retrieve all Unit objects
    serializer_class = UnitSerializer  # Use UnitSerializer for serialization

    def get_queryset(self):
        # Customize queryset based on user's role and permissions
        user = self.request.user
        if user.is_staff:
            match user.admin_user.admin_type.name:
                case "SUP":
                    return Unit.objects.all()
                case "INS":
                    return Unit.objects.filter(entity__instance=user.employee_user.instance)
                case "ENT":
                    return Unit.objects.filter(entity=user.employee_user.entity)
                case "UNI":
                    return Unit.objects.filter(unit=user.employee_user.unit)
        return Unit.objects.filter(entity=user.employee_user.entity)
