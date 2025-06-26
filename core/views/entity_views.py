from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from core.models.entity import Entity
from core.models.instance import Instance
from core.models.unit import Unit
from django.contrib.contenttypes.models import ContentType
from core.serializers.entity_serializers import EntitySerializer
from core.permissions import ReadOnlyUnlessSuperadmin
from rest_framework.response import Response
from core.permissions.hierachial_permissions import HierarchicalOrgPermission
from core.models.organisation_role import OrganisationRole
from core.utils.permissions import get_organisation_id_from_request

class EntityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Entities:
    - All authenticated users can read (GET) entities based on their permissions
    - Only superadmins can create/update/delete entities
    """
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer
    permission_classes = [IsAuthenticated, HierarchicalOrgPermission]

    def get_object(self):
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj


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
        Returns entities based on user's permissions:
        - Superadmin: all entities
        - Instance admin: entities in their instance
        - Entity admin: their entity and child entities
        - Unit admin: entities associated with their unit
        - Regular users: entities they belong to
        """
        user = self.request.user

        # Check if the user is staff and has an admin profile
        if user.is_staff and hasattr(user, 'admin_user'):
            admin_user = user.admin_user
            admin_type_name = admin_user.admin_type.name
            jurisdiction = admin_user.jurisdiction

            if admin_type_name == "SUP":
                # Superuser admin - return all entities
                return Entity.objects.all()
            elif admin_type_name == "INS" and isinstance(jurisdiction, Instance):
                # Instance admin - return entities in the same instance
                instance = jurisdiction
                return Entity.objects.filter(instance=instance)
            elif admin_type_name == "ENT" and isinstance(jurisdiction, Entity):
                # Entity admin - return their entity and child entities
                entity = jurisdiction
                return self.get_all_entities(entity)
            elif admin_type_name == "UNI" and isinstance(jurisdiction, Unit):
                # Unit admin - return entities associated with their unit
                unit = jurisdiction
                return Entity.objects.filter(units=unit)
            else:
                return Entity.objects.none()
        else:
            # Regular users can only see their own entity
            if hasattr(user, 'employee_user'):
                return Entity.objects.filter(id=user.employee_user.entity.id)
            return Entity.objects.none()

    def get_all_entities(self, parent_entity):
        """
        Recursive function to get all descendant entities
        """
        entities = [parent_entity]
        child_entities = Entity.objects.filter(parent_entity=parent_entity)
        for child in child_entities:
            entities.extend(self.get_all_entities(child))
        return entities

    