from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from core.models.organisation_chart import OrganisationChart
from core.models.organisation_chart_position_assignment import OrganisationChartPositionAssignment
from core.serializers.organisation_chart_serializers import (
    OrganisationChartSerializer,
    OrganisationChartListSerializer,
    OrganisationChartSimpleSerializer
)
from core.serializers.organisation_chart_position_assignment_serializers import (
    OrganisationChartPositionAssignmentSerializer,
    OrganisationChartPositionListSerializer
)


class OrganisationChartViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing organization charts
    """
    queryset = OrganisationChart.objects.all()
    serializer_class = OrganisationChartSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['entityID', 'Suspended', 'Lapsed']
    search_fields = ['orgChartName', 'entityID__name']
    ordering_fields = ['orgChartName', 'DateAdded', 'LastUpdate']
    ordering = ['-DateAdded']

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'list':
            return OrganisationChartListSerializer
        elif self.action == 'simple_list':
            return OrganisationChartSimpleSerializer
        return OrganisationChartSerializer

    def get_queryset(self):
        """
        Get the list of items for this view.
        Filter by entity if specified
        """
        queryset = super().get_queryset()
        entity_id = self.request.query_params.get('entity', None)
        if entity_id:
            queryset = queryset.filter(entityID=entity_id)
        return queryset

    def perform_create(self, serializer):
        """Create a new organization chart"""
        serializer.save(
            LastUpdatedByID=self.request.user,
            created_by=self.request.user
        )

    def perform_update(self, serializer):
        """Update an organization chart"""
        serializer.save(LastUpdatedByID=self.request.user)

    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        """Suspend an organization chart"""
        org_chart = self.get_object()
        org_chart.suspend()
        return Response({'status': 'Organization chart suspended'})

    @action(detail=True, methods=['post'])
    def unsuspend(self, request, pk=None):
        """Unsuspend an organization chart"""
        org_chart = self.get_object()
        org_chart.unsuspend()
        return Response({'status': 'Organization chart unsuspended'})

    @action(detail=True, methods=['post'])
    def lapse(self, request, pk=None):
        """Mark an organization chart as lapsed"""
        org_chart = self.get_object()
        org_chart.lapse()
        return Response({'status': 'Organization chart marked as lapsed'})

    @action(detail=True, methods=['post'])
    def unlapse(self, request, pk=None):
        """Remove lapsed status from an organization chart"""
        org_chart = self.get_object()
        org_chart.unlapse()
        return Response({'status': 'Organization chart unmarked as lapsed'})

    @action(detail=True)
    def positions(self, request, pk=None):
        """Get all positions in an organization chart"""
        org_chart = self.get_object()
        positions = org_chart.position_assignments.all()
        serializer = OrganisationChartPositionListSerializer(positions, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def statistics(self, request, pk=None):
        """Get detailed statistics for an organization chart"""
        org_chart = self.get_object()
        positions = org_chart.position_assignments.all()
        
        stats = {
            'total_positions': positions.count(),
            'active_positions': positions.filter(Suspended='N', Lapsed='N').count(),
            'suspended_positions': positions.filter(Suspended='Y').count(),
            'lapsed_positions': positions.filter(Lapsed='Y').count(),
            'hierarchy_levels': positions.values('positionLevel').annotate(
                count=Count('positionLevel')
            ),
            'top_level_positions': positions.filter(positionParentID=0).count(),
        }
        
        return Response(stats)

    @action(detail=True)
    def hierarchy(self, request, pk=None):
        """Get hierarchical structure of the organization chart"""
        org_chart = self.get_object()
        
        def build_hierarchy(parent_id=0):
            positions = org_chart.position_assignments.filter(positionParentID=parent_id)
            return [
                {
                    'id': pos.positionID,
                    'title': pos.positionTitle,
                    'level': pos.positionLevel,
                    'code': pos.positionCode,
                    'subordinates': build_hierarchy(pos.positionID)
                }
                for pos in positions
            ]
        
        hierarchy = build_hierarchy()
        return Response(hierarchy)

    @action(detail=False)
    def simple_list(self, request):
        """Get simplified list of organization charts"""
        queryset = self.get_queryset()
        serializer = OrganisationChartSimpleSerializer(queryset, many=True)
        return Response(serializer.data)


class OrganisationChartPositionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing position assignments within organization charts
    """
    queryset = OrganisationChartPositionAssignment.objects.all()
    serializer_class = OrganisationChartPositionAssignmentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['orgChartID', 'entityID', 'Suspended', 'Lapsed', 'positionLevel']
    search_fields = ['positionTitle', 'positionCode', 'positionDescription']
    ordering_fields = ['positionOrder', 'positionLevel', 'positionTitle', 'DateAdded']
    ordering = ['positionOrder', 'positionLevel', 'positionTitle']

    def get_queryset(self):
        """
        Get the list of items for this view.
        Filter by org chart if specified
        """
        queryset = super().get_queryset()
        org_chart_id = self.request.query_params.get('org_chart', None)
        if org_chart_id:
            queryset = queryset.filter(orgChartID=org_chart_id)
        return queryset

    def perform_create(self, serializer):
        """Create a new position assignment"""
        serializer.save(
            LastUpdatedByID=self.request.user,
            created_by=self.request.user
        )

    def perform_update(self, serializer):
        """Update a position assignment"""
        serializer.save(LastUpdatedByID=self.request.user)

    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        """Suspend a position"""
        position = self.get_object()
        position.suspend()
        return Response({'status': 'Position suspended'})

    @action(detail=True, methods=['post'])
    def unsuspend(self, request, pk=None):
        """Unsuspend a position"""
        position = self.get_object()
        position.unsuspend()
        return Response({'status': 'Position unsuspended'})

    @action(detail=True)
    def subordinates(self, request, pk=None):
        """Get all subordinate positions"""
        position = self.get_object()
        subordinates = position.get_subordinates()
        serializer = OrganisationChartPositionListSerializer(subordinates, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def superior(self, request, pk=None):
        """Get superior position"""
        position = self.get_object()
        superior = position.get_superior()
        if superior:
            serializer = OrganisationChartPositionListSerializer(superior)
            return Response(serializer.data)
        return Response({'message': 'No superior position found'}, status=status.HTTP_404_NOT_FOUND)