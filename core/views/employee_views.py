from core.models.employee import Employee
from core.models.admin import Admin
from core.serializers.employee_serializers import EmployeeSerializer
from rest_framework import viewsets
from django.shortcuts import get_object_or_404

# Define a viewset for managing Employee objects
class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()  # Retrieve all Employee objects
    serializer_class = EmployeeSerializer  # Use EmployeeSerializer for serialization

    def get_queryset(self):
        # Customize queryset based on the user's role and permissions
        user = self.request.user
        if user.is_staff:
            # Filter based on the admin type of the user if they are staff
            match user.admin_user.admin_type.name:
                case "SUP":
                    return Employee.objects.all()
                case "INS":
                    return Employee.objects.filter(instance=user.employee_user.instance)
                case "ENT":
                    return Employee.objects.filter(entity=user.employee_user.entity)
                case "UNI":
                    return Employee.objects.filter(unit=user.employee_user.unit)
        # Default filtering for non-staff users
        return Employee.objects.filter(entity=user.employee_user.entity)

    def destroy(self, request, pk=None):
        # Handle deletion of a specific Employee object by primary key
        user = get_object_or_404(Admin, pk=pk)
