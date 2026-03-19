from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser  # ✅ Added parsers for file uploads
from django.db.models import Q

from hub.models.absence import Absence
from hub.serializers.absence_serializer import AbsenceSerializer


class AbsenceViewSet(viewsets.ModelViewSet):
    """
    Any authenticated user has full CRUD access to Absences.
    """
    queryset = Absence.objects.all()
    serializer_class = AbsenceSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)  # ✅ Allows handling of file uploads

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Absence.objects.all()
        return Absence.objects.none()

    def create(self, request, *args, **kwargs):
        """
        Overridden create to set some fields based on the current user.
        """
        data = request.data.copy()
        data['user'] = request.user.id
        data['last_updated_by_id'] = request.user.id
        data['created_by_id'] = request.user.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        """
        Overridden update to set tracking fields.
        """
        instance = self.get_object()
        data = request.data.copy()
        data['last_updated_by_id'] = request.user.id

        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
