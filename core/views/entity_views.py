from rest_framework import viewsets
from core.models.entity import Entity
from core.serializers.entity_serializers import EntitySerializer
from django.db import models


# Define a viewset for managing Entity objects
class EntityViewSet(viewsets.ModelViewSet):
    queryset = Entity.objects.all()  # Retrieve all Entity objects
    serializer_class = EntitySerializer  # Use EntitySerializer for serialization

    def get_queryset(self):
        # Customize queryset based on user's role and permissions
        user = self.request.user
        if user.is_staff:
            match user.admin_user.admin_type.name:
                case "SUP":
                    return Entity.objects.all()
                case "INS":
                    return Entity.objects.filter(instance=user.employee_user.instance)
                case "ENT":
                    return Entity.objects.filter(
                        models.Q(id=user.employee_user.entity.id) | models.Q(parent_entity=user.employee_user.entity)
                    )
                case "UNI":
                    return Entity.objects.filter(entity=user.employee_user.entity)
        return Entity.objects.filter(entity=user.employee_user.entity)
