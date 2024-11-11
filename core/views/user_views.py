from core.models.user import User
from core.models.instance import Instance
from core.models.entity import Entity
from core.models.unit import Unit
from django.contrib.contenttypes.models import ContentType

from core.serializers.user_serializers import UserSerializer
from rest_framework import viewsets
from django.db import models




# Define a viewset for managing User objects
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()  # Retrieve all User objects
    serializer_class = UserSerializer  # Use UserSerializer for serialization


    def get_queryset(self):
        user = self.request.user

        # Check if the user is staff and has an admin profile
        if user.is_staff and hasattr(user, 'admin_user'):
            admin_user = user.admin_user
            admin_type_name = admin_user.admin_type.name
            jurisdiction = admin_user.jurisdiction  # Can be Instance, Entity, or Unit

            if admin_type_name == "SUP":
                # Superuser admin - return all users
                return User.objects.all()
            elif admin_type_name == "INS" and isinstance(jurisdiction, Instance):
                # Instance admin - return users in the same instance
                instance = jurisdiction
                return User.objects.filter(
                    models.Q(employee_user__instance=instance) |
                    models.Q(admin_user__jurisdiction_content_type=ContentType.objects.get_for_model(Instance),
                      admin_user__jurisdiction_object_id=instance.id)
                ).distinct()
            elif admin_type_name == "ENT" and isinstance(jurisdiction, Entity):
                # Entity admin - return users in the same entity and child entities
                entity = jurisdiction
                # Get all descendant entities
                all_entities = self.get_all_entities(entity)
                entity_ids = [e.id for e in all_entities]

                return User.objects.filter(
                    models.Q(employee_user__entity__in=all_entities) |
                    models.Q(admin_user__jurisdiction_content_type=ContentType.objects.get_for_model(Entity),
                      admin_user__jurisdiction_object_id__in=entity_ids)
                ).distinct()
            elif admin_type_name == "UNI" and isinstance(jurisdiction, Unit):
                # Unit admin - return users in the same unit
                unit = jurisdiction
                return User.objects.filter(
                    models.Q(employee_user__unit=unit) |
                    models.Q(admin_user__jurisdiction_content_type=ContentType.objects.get_for_model(Unit),
                      admin_user__jurisdiction_object_id=unit.id)
                ).distinct()
            else:
                return User.objects.none()
        else:
            # Non-staff users can only see themselves
            return User.objects.filter(pk=user.pk)

    def get_all_entities(self, parent_entity):
        # Recursive function to get all descendant entities
        entities = [parent_entity]
        child_entities = Entity.objects.filter(parent_entity=parent_entity)
        for child in child_entities:
            entities.extend(self.get_all_entities(child))
        return entities
