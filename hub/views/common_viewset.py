from rest_framework import viewsets, status
from rest_framework.response import Response


class CommonViewSet(viewsets.ModelViewSet):
    def create(self, request, *args, **kwargs):
        # Make a mutable copy of the request data
        data = request.data.copy()
        # Set the user field to the logged-in user

        data['last_updated_by_id'] = request.user.id
        data['created_by_id'] = request.user.id

        if 'entity' not in data or not data['entity']:
            if hasattr(request.user, 'employee_user') and request.user.employee_user.entity:
                data['entity'] = request.user.employee_user.entity.id
            else:
                data['entity'] = None

        if 'unit' not in data or not data['unit']:
            if hasattr(request.user, 'employee_user') and request.user.employee_user.unit:
                data['unit'] = request.user.employee_user.unit.id
            else:
                data['unit'] = None
        # Fetch the task instance

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
   