from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Q
from rest_framework import status
from rest_framework.decorators import action
from django.utils.timezone import now
from datetime import timedelta

# Models & Serializers
from hub.models.project import Project
from hub.models.work_entries import WorkEntries
from hub.models.task import Task
from hub.serializers.project_serializer import ProjectSerializer
from hub.serializers.work_entries_serializer import WorkEntriesSerializer
from core.serializers.employee_serializers import EmployeeSerializer

from .common_viewset import CommonViewSet


class ProjectViewSet(CommonViewSet):
    """
    Any authenticated user has full CRUD access to Projects.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Any logged-in user sees all Projects
        if user.is_authenticated:
            return Project.objects.all()
        return Project.objects.none()

    @action(detail=True, methods=['get'], url_path='members')
    def get_project_members(self, request, pk=None):
        """
        Custom action to retrieve project members.
        """
        try:
            project = self.get_object()
            members = project.members.all()
            serializer = EmployeeSerializer(members, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response({'detail': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'], url_path='work-entries')
    def get_work_entries(self, request, pk=None):
        """
        Custom action to retrieve all work entries for a project,
        plus the total duration of those entries.
        """
        try:
            project = self.get_object()
            work_entries = WorkEntries.objects.filter(project=project)

            total_duration = work_entries.aggregate(total_duration=Sum('duration'))['total_duration'] or timedelta(0)
            if isinstance(total_duration, timedelta):
                total_seconds = int(total_duration.total_seconds())
            else:
                total_seconds = total_duration  # if already int/seconds

            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            formatted_total = f"{hours}h {minutes}m"

            serializer = WorkEntriesSerializer(work_entries, many=True)
            response_data = {
                'work_entries': serializer.data,
                'total_duration': formatted_total
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response({'detail': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='dashboard')
    def get_projects_dashboard(self, request, *args, **kwargs):
        """
        Example dashboard-like summary for all projects (since all users have full access now).
        """
        current_date = now()

        # Ongoing projects
        ongoing_projects = Project.objects.filter(
            Q(start_date__lte=current_date) & (Q(end_date__gte=current_date) | Q(end_date__isnull=True)),
            is_deleted=False
        ).count()

        # Estimated project value
        estimated_project_value = Project.objects.filter(
            Q(start_date__lte=current_date) & (Q(end_date__gte=current_date) | Q(end_date__isnull=True)),
            is_deleted=False
        ).aggregate(total_value=Sum('project_value'))['total_value'] or 0

        # Projects needing attention
        projects_needing_attention = Task.objects.filter(
            project__in=Project.objects.filter(
                Q(start_date__lte=current_date) & (Q(end_date__gte=current_date) | Q(end_date__isnull=True)),
                is_deleted=False
            ),
            task_status__name__in=["IN_PROGRESS", "PENDING"],
            is_deleted=False
        ).count()

        # Completed projects this month
        completed_this_month = Project.objects.filter(
            end_date__month=current_date.month,
            end_date__year=current_date.year,
            is_deleted=False
        ).count()

        # Completion rate
        total_opportunities = ongoing_projects
        completion_rate = (completed_this_month / total_opportunities * 100) if total_opportunities else 0

        return Response({
            "projects_ongoing_this_month": ongoing_projects,
            "estimated_project_value": f"{estimated_project_value:.2f} €",
            "projects_needing_attention": projects_needing_attention,
            "completion_rate_this_month": f"{completion_rate:.0f} %",
        })
