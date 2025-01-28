from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.db.models import Sum

# Models & Serializers
from hub.models.project_phase import ProjectPhase
from hub.models.work_entries import WorkEntries
from hub.serializers.project_phase_serializer import ProjectPhaseSerializer
from hub.serializers.work_entries_serializer import WorkEntriesSerializer
from core.serializers.employee_serializers import EmployeeSerializer

from .common_viewset import CommonViewSet


class ProjectPhaseViewSet(CommonViewSet):
    """
    Any authenticated user has full CRUD access to ProjectPhases.
    """
    queryset = ProjectPhase.objects.all()
    serializer_class = ProjectPhaseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return ProjectPhase.objects.all()
        return ProjectPhase.objects.none()

    @action(detail=True, methods=['get'], url_path='members')
    def get_project_members(self, request, pk=None):
        """
        Custom action to retrieve project phase members.
        """
        try:
            phase = self.get_object()
            members = phase.members.all()
            serializer = EmployeeSerializer(members, many=True)
            return Response(serializer.data, status=200)
        except ProjectPhase.DoesNotExist:
            return Response({'detail': 'Project phase not found.'}, status=404)

    @action(detail=True, methods=['get'], url_path='work-entries')
    def get_work_entries(self, request, pk=None):
        """
        Custom action to retrieve work entries related to a project phase.
        """
        try:
            phase = self.get_object()
            work_entries = WorkEntries.objects.filter(project=phase.project)

            total_duration = work_entries.aggregate(total_duration=Sum('duration'))['total_duration'] or 0
            hours = total_duration // 3600
            minutes = (total_duration % 3600) // 60
            formatted_total_duration = f"{int(hours)}h {int(minutes)}m"

            serializer = WorkEntriesSerializer(work_entries, many=True)
            response_data = {
                'work_entries': serializer.data,
                'total_duration': formatted_total_duration
            }

            return Response(response_data, status=200)
        except ProjectPhase.DoesNotExist:
            return Response({'detail': 'Project not found.'}, status=404)
