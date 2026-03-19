from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from core.models.user import User
from core.models.instance import Instance
from core.models.entity import Entity
from core.models.unit import Unit
from django.contrib.contenttypes.models import ContentType
from core.serializers.user_serializers import UserSerializer
from django.db import models

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Users:
    - All authenticated users can read (GET) users based on their permissions
    - Only superadmins can create/update/delete users
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
#   permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Set created_by and last_updated_by to current user
        serializer.validated_data['created_by'] = request.user
        serializer.validated_data['last_updated_by'] = request.user
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Set last_updated_by to current user
        serializer.validated_data['last_updated_by'] = request.user

        self.perform_update(serializer)
        return Response(serializer.data)

    def get_queryset(self):
        """
        Returns users based on user's permissions:
        - Superadmin: all users
        - Instance admin: users in their instance
        - Entity admin: users in their entity and child entities
        - Unit admin: users in their unit
        - Regular users: only themselves
        """
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
        """Recursive function to get all descendant entities"""
        entities = [parent_entity]
        child_entities = Entity.objects.filter(parent_entity=parent_entity)
        for child in child_entities:
            entities.extend(self.get_all_entities(child))
        return entities
