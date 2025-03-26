from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser  # Added parsers for file uploads
from hub.models.work_entries import WorkEntries
from hub.serializers.work_entries_serializer import WorkEntriesSerializer
from hub.models.task import Task  # Only needed if you're auto-filling from Task


class WorkEntriesViewSet(viewsets.ModelViewSet):
    """
    Any authenticated user can CRUD (create, read, update, delete) WorkEntries.
    """
    queryset = WorkEntries.objects.all()
    serializer_class = WorkEntriesSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)  # To handle file uploads

    def get_queryset(self):
        """
        Return all WorkEntries for any logged-in user.
        """
        user = self.request.user
        if user.is_authenticated:
            return WorkEntries.objects.all()
        return WorkEntries.objects.none()

    def create(self, request, *args, **kwargs):
        """
        Override create to set certain fields (user, last_updated_by_id, created_by_id) from the request.
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
        Override update to set 'last_updated_by_id' and optionally auto-fill from the Task.
        """
        instance = self.get_object()
        data = request.data.copy()
        data['last_updated_by_id'] = request.user.id

        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
