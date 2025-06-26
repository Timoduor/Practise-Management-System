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
from core.permissions.hierachial_permissions import HierarchicalOrgPermission
from core.models.organisation_role import OrganisationRole
from core.utils.permissions import get_organisation_id_from_request


class OrganisationChartViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing organization charts
    """
    queryset = OrganisationChart.objects.all()
    serializer_class = OrganisationChartSerializer
    permission_classes = [IsAuthenticated, HierarchicalOrgPermission]
    filterset_fields = ['entityID', 'Suspended', 'Lapsed']
    search_fields = ['orgChartName', 'entityID__entityName']
    ordering_fields = ['orgChartName', 'DateAdded', 'LastUpdate']
    ordering = ['-DateAdded']

    def get_object(self):
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj
 

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
        serializer.save(LastUpdatedByID=self.request.user)

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
        
        # Group by position level
        level_stats = list(positions.values('positionLevel')
                          .annotate(count=Count('positionLevel'))
                          .order_by('positionLevel'))
        
        # Count top-level positions (those with no parent)
        top_level_count = positions.filter(positionParentID__isnull=True).count()
        
        stats = {
            'total_positions': positions.count(),
            'active_positions': positions.filter(Suspended='N', Lapsed='N').count(),
            'suspended_positions': positions.filter(Suspended='Y').count(),
            'lapsed_positions': positions.filter(Lapsed='Y').count(),
            'hierarchy_levels': level_stats,
            'top_level_positions': top_level_count,
        }
        
        return Response(stats)

    @action(detail=True)
    def hierarchy(self, request, pk=None):
        """Get hierarchical structure of the organization chart"""
        org_chart = self.get_object()
        
        def build_hierarchy(parent=None):
            # Filter positions that have this parent
            if parent is None:
                # Get top-level positions (no parent)
                positions = org_chart.position_assignments.filter(positionParentID__isnull=True)
            else:
                # Get subordinates of this parent
                positions = parent.subordinates.all()
            
            return [
                {
                    'id': pos.positionAssignmentID,
                    'title': pos.positionTitle,
                    'level': pos.positionLevel,
                    'code': pos.positionCode,
                    'order': pos.positionOrder,
                    'subordinates': build_hierarchy(pos)
                }
                for pos in positions.order_by('positionOrder', 'positionTitle')
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
    filterset_fields = ['orgChartID', 'Suspended', 'Lapsed', 'positionLevel']
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
        serializer.save(LastUpdatedByID=self.request.user)

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

    @action(detail=True, methods=['post'])
    def lapse(self, request, pk=None):
        """Mark a position as lapsed"""
        position = self.get_object()
        position.lapse()
        return Response({'status': 'Position marked as lapsed'})

    @action(detail=True, methods=['post'])
    def unlapse(self, request, pk=None):
        """Remove lapsed status from a position"""
        position = self.get_object()
        position.unlapse()
        return Response({'status': 'Position unmarked as lapsed'})

    @action(detail=True)
    def subordinates(self, request, pk=None):
        """Get all subordinate positions"""
        position = self.get_object()
        subordinates = position.subordinates.all()
        serializer = OrganisationChartPositionListSerializer(subordinates, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def superior(self, request, pk=None):
        """Get superior position"""
        position = self.get_object()
        superior = position.positionParentID  # Direct access to parent via FK
        if superior:
            serializer = OrganisationChartPositionListSerializer(superior)
            return Response(serializer.data)
        return Response({'message': 'No superior position found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def reorder(self, request, pk=None):
        """Change the order of a position among its siblings"""
        position = self.get_object()
        new_order = request.data.get('order')
        
        if new_order is not None:
            try:
                # Update order
                position.positionOrder = int(new_order)
                position.save()
                return Response({
                    'status': 'Position reordered successfully', 
                    'new_order': position.positionOrder
                })
            except ValueError:
                return Response(
                    {'error': 'Invalid order value'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            {'error': 'Order value required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )