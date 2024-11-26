from core.models.admin import Admin
from core.models.instance import Instance
from core.models.entity import Entity
from core.models.unit import Unit
from django.contrib.contenttypes.models import ContentType
from core.serializers.admin_serializers import AdminSerializer
from rest_framework import viewsets, status  # Import status here
from django.db import models
from rest_framework.response import Response


# Define a viewset for managing Admin objects
class AdminViewSet(viewsets.ModelViewSet):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer

    def create(self, request):
        # Handle user creation with validation and response
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Raise exception if data is invalid
        self.perform_create(serializer)  # Save new user
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        # Customize queryset based on the user's role and permissions
        user = self.request.user

        # Check if the user is staff and has an admin profile
        if user.is_staff and hasattr(user, 'admin_user'):
            admin_user = user.admin_user
            admin_type_name = admin_user.admin_type.name
            jurisdiction = admin_user.jurisdiction  # Can be Instance, Entity, or Unit

            if admin_type_name == "SUP":
                # Superuser admin - return all admins
                return Admin.objects.all()
            elif admin_type_name == "INS" and isinstance(jurisdiction, Instance):
                # Instance admin - return admins in the same instance
                instance = jurisdiction
                return Admin.objects.filter(
                    models.Q(jurisdiction_content_type=ContentType.objects.get_for_model(Instance),
                      jurisdiction_object_id=instance.id) |
                    models.Q(user__employee_user__instance=instance)
                ).distinct()
            elif admin_type_name == "ENT" and isinstance(jurisdiction, Entity):
                # Entity admin - return admins in the same entity and child entities
                entity = jurisdiction
                # Get all descendant entities
                all_entities = self.get_all_entities(entity)
                entity_ids = [e.id for e in all_entities]

                return Admin.objects.filter(
                    models.Q(jurisdiction_content_type=ContentType.objects.get_for_model(Entity),
                      jurisdiction_object_id__in=entity_ids) |
                    models.Q(user__employee_user__entity__in=all_entities)
                ).distinct()
            elif admin_type_name == "UNI" and isinstance(jurisdiction, Unit):
                # Unit admin - return admins in the same unit
                unit = jurisdiction
                return Admin.objects.filter(
                    models.Q(jurisdiction_content_type=ContentType.objects.get_for_model(Unit),
                      jurisdiction_object_id=unit.id) |
                    models.Q(user__employee_user__unit=unit)
                ).distinct()
            else:
                return Admin.objects.none()
        else:
            # Non-staff users should not see any admins
            return Admin.objects.none()

    def get_all_entities(self, parent_entity):
        # Recursive function to get all descendant entities
        entities = [parent_entity]
        child_entities = Entity.objects.filter(parent_entity=parent_entity)
        for child in child_entities:
            entities.extend(self.get_all_entities(child))
        return entities
