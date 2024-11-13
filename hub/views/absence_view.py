from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from hub.models.task import Task
from rest_framework import viewsets, status
from hub.models.absence import Absence
from hub.serializers.absence_serializer import AbsenceSerializer
from django.db.models import Q



class AbsenceViewSet(viewsets.ModelViewSet):
    queryset = Absence.objects.all()
    serializer_class = AbsenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            match user.admin_user.admin_type.name:
                case "SUP":
                  return Absence.objects.all()
                case "INS":
                  return Absence.objects.filter(Q(project__entity__instance= user.employee_user.instance) |
                                                  Q(sale__entity__instance = user.employee_user.instance ))   
                case "ENT":
                    return Absence.objects.filter(Q(project__entity= user.employee_user.entity) |
                                                  Q(sale__entity = user.employee_user.entity ))    
                case "UNI":
                    return Absence.objects.filter(Q(project__unit= user.employee_user.unit) |
                                                  Q(sale__unit = user.employee_user.unit ))   

        return Absence.objects.filter(employee = user.employee_user)
    
    def create(self, request, *args, **kwargs):
        # Make a mutable copy of the request data
        data = request.data.copy()

        # Set the user field to the logged-in user
        data['user'] = request.user.id
        data['last_updated_by_id'] = request.user.id
        data['created_by_id'] = request.user.id

    
        # Pass the data to the serializer and validate it
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        # Save the data
        self.perform_create(serializer)

        # Return the response
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    
    def update(self, request, *args, **kwargs):
        # Get the instance to be updated using the primary key from URL kwargs
        instance = self.get_object()

        # Make a mutable copy of the request data
        data = request.data.copy()

        # Set the user fields to the logged-in user for tracking updates
        data['last_updated_by_id'] = request.user.id


        # Pass the data to the serializer along with the instance to update
        serializer = self.get_serializer(instance, data=data, partial=True)  # Use partial=True to allow partial updates
        serializer.is_valid(raise_exception=True)

        # Save the updated data
        self.perform_update(serializer)

        # Return the updated instance data as a response
        return Response(serializer.data, status=status.HTTP_200_OK)
            
