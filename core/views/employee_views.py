from core.models.employee import Employee
from core.models.admin import Admin
from core.models.instance import Instance
from core.models.entity import Entity
from core.models.unit import Unit
from django.contrib.contenttypes.models import ContentType
from core.serializers.employee_serializers import EmployeeSerializer
from rest_framework import viewsets, status
from django.db import models
from rest_framework.response import Response

# Define a viewset for managing Employee objects
class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

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
        user = self.request.user

        # Check if the user is staff and has an admin profile
        if user.is_staff and hasattr(user, 'admin_user'):
            admin_user = user.admin_user
            admin_type_name = admin_user.admin_type.name
            jurisdiction = admin_user.jurisdiction

            if admin_type_name == "SUP":
                # Superuser admin - return all employees
                return Employee.objects.all()
            elif admin_type_name == "INS" and isinstance(jurisdiction, Instance):
                # Instance admin - return employees in the same instance
                instance = jurisdiction
                return Employee.objects.filter(instance=instance)
            elif admin_type_name == "ENT" and isinstance(jurisdiction, Entity):
                # Entity admin - return employees in the same entity and child entities
                entity = jurisdiction
                # Get all descendant entities
                all_entities = self.get_all_entities(entity)
                return Employee.objects.filter(entity__in=all_entities)
            elif admin_type_name == "UNI" and isinstance(jurisdiction, Unit):
                # Unit admin - return employees in the same unit
                unit = jurisdiction
                return Employee.objects.filter(unit=unit)
            else:
                return Employee.objects.none()
        else:
            # Non-staff users can only see employees in their entity
            return Employee.objects.filter(entity=user.employee_user.entity)

    def get_all_entities(self, parent_entity):
        # Recursive function to get all descendant entities
        entities = [parent_entity]
        child_entities = Entity.objects.filter(parent_entity=parent_entity)
        for child in child_entities:
            entities.extend(self.get_all_entities(child))
        return entities
