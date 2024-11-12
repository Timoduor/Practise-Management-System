from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from hub.models.project import Project
from django.db.models import Sum
from rest_framework import  status
from rest_framework.decorators import action
from .common_viewset import CommonViewSet
from hub.serializers.project_serializer import ProjectSerializer
from django.db.models import Q
from django.utils.timezone import now
from hub.models.task import Task


class ProjectViewSet(CommonViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            match user.admin_user.admin_type.name:
                case "SUP":
                  return Project.objects.all()
                case "INS":
                  return Project.objects.filter(entity__instance = user.employee_user.instance)
                case "ENT":
                    return Project.objects.filter(project__entity= user.employee_user.entity)  
                case "UNI":
                    return Project.objects.filter(project__unit= user.employee_user.unit)

        return Project.objects.filter(entity= user.employee_user.entity) 
    
    @action(detail=True, methods=['get'], url_path='members')
    def get_project_members(self, request, pk=None):
        try:
            # Fetch the sale by its primary key (pk)
            project = self.get_object()
            # Get the members associated with the sale
            members = project.members.all()
            # Serialize the members
            serializer = EmployeeSerializer(members, many=True)
            # Return the serialized data
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response({'detail': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'], url_path='work-entries')
    def get_work_entries(self, request, pk=None):
        try:
            # Fetch the project by its primary key (pk)
            project = self.get_object()
            # Get the work entries related to the project
            work_entries = WorkEntries.objects.filter(project=project)

            # Aggregate the total duration of all work entries for the project
            total_duration = work_entries.aggregate(total_duration=Sum('duration'))['total_duration'] or timedelta(0)

            # If total_duration is a timedelta, convert it to total seconds
            if isinstance(total_duration, timedelta):
                total_seconds = int(total_duration.total_seconds())
            else:
                total_seconds = total_duration  # Assume it's already in seconds if not a timedelta

            # Convert total duration from seconds to hours and minutes
            total_duration_in_hours = total_seconds // 3600
            total_duration_in_minutes = (total_seconds % 3600) // 60
            formatted_total_duration = f"{int(total_duration_in_hours)}h {int(total_duration_in_minutes)}m"

            # Serialize the work entries
            serializer = WorkEntriesSerializer(work_entries, many=True)

            # Prepare the response data
            response_data = {
                'work_entries': serializer.data,
                'total_duration': formatted_total_duration
            }

            # Return the response with the serialized data and the total duration
            return Response(response_data, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response({'detail': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)

    


    @action(detail=False, methods=['get'], url_path='dashboard')
    def get_projects_dashboard(self, request, *args, **kwargs):
        user = self.request.user
        
        # Get the current date and extract month and year
        current_date = now()
         # Initialize filter dictionary based on admin type
        project_filter = {}

        # Apply filtering based on user’s admin level
        if user.is_staff:
            match user.admin_user.admin_type.name:
                case "SUP":
                    # SUP has access to all projects
                    pass
                case "INS":
                    project_filter = {"entity__instance": user.employee_user.instance}
                case "ENT":
                    project_filter = {"entity": user.employee_user.entity}
                case "UNI":
                    project_filter = {"unit": user.employee_user.unit}
        else:
            # Default filter for non-staff users
            project_filter = {"entity": user.employee_user.entity}


        # Ongoing projects (current date is between start_date and end_date)
        ongoing_projects = Project.objects.filter(
            Q(start_date_lte=current_date) & (Q(end_dategte=current_date) | Q(end_date_isnull=True)),
            is_deleted=False,
            **project_filter
        ).count()

        # Estimated project value for ongoing projects in the current month
        estimated_project_value = Project.objects.filter(
            Q(start_date_lte=current_date) & (Q(end_dategte=current_date) | Q(end_date_isnull=True)),
            is_deleted=False,
            **project_filter
        ).aggregate(total_value=Sum('project_value'))['total_value'] or 0

        # Projects with tasks needing attention (IN_PROGRESS or PENDING) for ongoing projects
        projects_needing_attention = Task.objects.filter(
            project__in=Project.objects.filter(
                Q(start_date_lte=current_date) & (Q(end_dategte=current_date) | Q(end_date_isnull=True)),
                is_deleted=False,
                **project_filter
            ),
            task_status__in=["IN_PROGRESS", "PENDING"],
            is_deleted=False
        ).count()

        # Total projects opportunities this month (ongoing projects)
        total_projects_opportunities = ongoing_projects

        # Completed projects count this month (projects with end date in the current month)
        completed_projects_count = Project.objects.filter(
            end_date__month=current_date.month,
            end_date__year=current_date.year,
            is_deleted=False,
            **project_filter
        ).count()

        # Calculate completion rate
        completion_rate = (completed_projects_count / total_projects_opportunities * 100) if total_projects_opportunities else 0

        return Response({
            "projects_ongoing_this_month": ongoing_projects,
            "estimated_project_value": f"{estimated_project_value:.2f} €",
            "projects_needing_attention": projects_needing_attention,
            "completion_rate_this_month": f"{completion_rate:.0f} %"
        })

