from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from hub.models.project import Project
from django.db.models import Sum
from hub.models.work_entries import WorkEntries
from rest_framework import  status
from core.serializers.employee_serializers import EmployeeSerializer
from hub.serializers.work_entries_serializer import WorkEntriesSerializer
from rest_framework.decorators import action
from .common_viewset import CommonViewSet
from hub.serializers.project_phase_serializer import ProjectPhaseSerializer
from hub.models.project_phase import ProjectPhase


class ProjectPhaseViewSet(CommonViewSet):
    queryset = ProjectPhase.objects.all()
    serializer_class = ProjectPhaseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            match user.admin_user.admin_type.name:
                case "SUP":
                  return ProjectPhase.objects.all()
                case "INS":
                  return ProjectPhase.objects.filter(entity__instance = user.employee_user.instance)
                case "ENT":
                    return ProjectPhase.objects.filter(project__entity= user.employee_user.entity)  
                case "UNI":
                    return ProjectPhase.objects.filter(project__unit= user.employee_user.unit)

        return ProjectPhase.objects.filter(project__project_members = user.employee_user) 
    
    @action(detail=True, methods=['get'], url_path='members')
    def get_project_members(self, request, pk=None):
        try:
            # Fetch the sale by its primary key (pk)
            phase = self.get_object()
            # Get the members associated with the sale
            members = phase.members.all()
            # Serialize the members
            serializer = EmployeeSerializer(members, many=True)
            # Return the serialized data
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ProjectPhase.DoesNotExist:
            return Response({'detail': 'Project phase not found.'}, status=status.HTTP_404_NOT_FOUND)
    

    @action(detail=True, methods=['get'], url_path='work-entries')
    def get_work_entries(self, request, pk=None):
        try:
            # Fetch the project by its primary key (pk)
            project = self.get_object()
            # Get the work entries related to the project
            work_entries = WorkEntries.objects.filter(project=project)

            # Aggregate the total duration (in seconds) of all work entries for the project
            total_duration = work_entries.aggregate(total_duration=Sum('duration'))['total_duration'] or 0


            # Convert total duration from seconds to hours and minutes
            total_duration_in_hours = total_duration // 3600
            total_duration_in_minutes = (total_duration % 3600) // 60
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

