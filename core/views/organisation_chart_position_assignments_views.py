from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from core.models.organisation_chart_position_assignment import OrganisationChartPositionAssignment
from core.serializers.organisation_chart_position_assignment_serializers import (
    OrganisationChartPositionAssignmentSerializer,
    OrganisationChartPositionListSerializer,
    OrganisationChartPositionSimpleSerializer
)


class OrganisationChartPositionAssignmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing position assignments within organization charts
    Provides CRUD operations and additional functionality for position management
    """
    queryset = OrganisationChartPositionAssignment.objects.all()
    serializer_class = OrganisationChartPositionAssignmentSerializer
    permission_classes = [IsAuthenticated]
    
    filterset_fields = {
        'orgChartID': ['exact'],
        'positionLevel': ['exact', 'in'],
        'Suspended': ['exact'],
        'Lapsed': ['exact'],
        'positionParentID': ['exact', 'isnull'],
        'DateAdded': ['gte', 'lte'],
        'LastUpdate': ['gte', 'lte'],
    }
    
    search_fields = [
        'positionTitle',
        'positionCode',
        'positionDescription',
        'orgChartID__orgChartName',
    ]
    
    ordering_fields = [
        'positionOrder',
        'positionLevel',
        'positionTitle',
        'DateAdded',
        'LastUpdate',
    ]
    
    ordering = ['positionOrder', 'positionLevel', 'positionTitle']

    def get_queryset(self):
        """
        Get the list of items for this view.
        Implements filtering by org chart and status
        """
        queryset = super().get_queryset()
        
        # Filter by org chart
        org_chart_id = self.request.query_params.get('org_chart', None)
        if org_chart_id:
            queryset = queryset.filter(orgChartID=org_chart_id)
            
        # Filter by entity (through org chart)
        entity_id = self.request.query_params.get('entity', None)
        if entity_id:
            queryset = queryset.filter(orgChartID__entityID=entity_id)
            
        # Filter by active status
        active_only = self.request.query_params.get('active_only', False)
        if active_only:
            queryset = queryset.filter(Suspended='N', Lapsed='N')
            
        # Filter by hierarchy level
        level = self.request.query_params.get('level', None)
        if level:
            queryset = queryset.filter(positionLevel=level)
            
        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'list':
            return OrganisationChartPositionListSerializer
        elif self.action == 'simple_list':
            return OrganisationChartPositionSimpleSerializer
        return OrganisationChartPositionAssignmentSerializer

    def perform_create(self, serializer):
        """Create a new position assignment with user tracking"""
        serializer.save(LastUpdatedByID=self.request.user)

    def perform_update(self, serializer):
        """Update a position assignment with user tracking"""
        serializer.save(LastUpdatedByID=self.request.user)

    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        """Suspend a position"""
        position = self.get_object()
        position.suspend()
        return Response({
            'status': 'success',
            'message': f'Position {position.positionTitle} has been suspended'
        })

    @action(detail=True, methods=['post'])
    def unsuspend(self, request, pk=None):
        """Unsuspend a position"""
        position = self.get_object()
        position.unsuspend()
        return Response({
            'status': 'success',
            'message': f'Position {position.positionTitle} has been unsuspended'
        })

    @action(detail=True, methods=['post'])
    def lapse(self, request, pk=None):
        """Mark a position as lapsed"""
        position = self.get_object()
        position.lapse()
        return Response({
            'status': 'success',
            'message': f'Position {position.positionTitle} has been marked as lapsed'
        })

    @action(detail=True, methods=['post'])
    def unlapse(self, request, pk=None):
        """Remove lapsed status from a position"""
        position = self.get_object()
        position.unlapse()
        return Response({
            'status': 'success',
            'message': f'Position {position.positionTitle} has been unmarked as lapsed'
        })

    @action(detail=True)
    def subordinates(self, request, pk=None):
        """Get all subordinate positions"""
        position = self.get_object()
        subordinates = position.subordinates.all()  # Use the related_name from the FK
        
        # Include recursive subordinates if requested
        recursive = request.query_params.get('recursive', False)
        if recursive:
            def get_recursive_subordinates(positions):
                result = []
                for pos in positions:
                    result.append(pos)
                    result.extend(get_recursive_subordinates(pos.subordinates.all()))
                return result
                
            subordinates = get_recursive_subordinates(subordinates)
            
        serializer = OrganisationChartPositionListSerializer(subordinates, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def superior(self, request, pk=None):
        """Get superior position"""
        position = self.get_object()
        superior = position.positionParentID  # Direct access via FK
        
        if superior:
            serializer = OrganisationChartPositionAssignmentSerializer(superior)
            return Response(serializer.data)
        return Response({
            'message': 'This is a top-level position'
        }, status=status.HTTP_200_OK)

    @action(detail=True)
    def hierarchy_chain(self, request, pk=None):
        """Get the complete hierarchy chain for this position"""
        position = self.get_object()
        chain = []
        current = position
        
        # Build chain up to top level
        while current:
            chain.append(current)
            current = current.positionParentID  # Direct access via FK
            
        serializer = OrganisationChartPositionListSerializer(chain, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def statistics(self, request):
        """Get statistics about positions"""
        queryset = self.get_queryset()
        
        stats = {
            'total_positions': queryset.count(),
            'active_positions': queryset.filter(Suspended='N', Lapsed='N').count(),
            'suspended_positions': queryset.filter(Suspended='Y').count(),
            'lapsed_positions': queryset.filter(Lapsed='Y').count(),
            'by_level': queryset.values('positionLevel').annotate(
                count=Count('positionLevel')
            ).order_by('positionLevel'),
            'top_level_positions': queryset.filter(positionParentID__isnull=True).count(),  # Changed to check null
        }
        
        return Response(stats)

    @action(detail=False)
    def search(self, request):
        """Advanced search endpoint"""
        queryset = self.get_queryset()
        
        # Search parameters
        title = request.query_params.get('title', None)
        code = request.query_params.get('code', None)
        level = request.query_params.get('level', None)
        has_subordinates = request.query_params.get('has_subordinates', None)
        
        if title:
            queryset = queryset.filter(positionTitle__icontains=title)
        if code:
            queryset = queryset.filter(positionCode__icontains=code)
        if level:
            queryset = queryset.filter(positionLevel=level)
        if has_subordinates is not None:
            if has_subordinates.lower() == 'true':
                queryset = queryset.filter(subordinates__isnull=False).distinct()  # Updated related_name
            else:
                queryset = queryset.filter(subordinates__isnull=True)  # Updated related_name
                
        serializer = OrganisationChartPositionListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def simple_list(self, request):
        """Get simplified list of positions"""
        queryset = self.get_queryset()
        serializer = OrganisationChartPositionSimpleSerializer(queryset, many=True)
        return Response(serializer.data)
        
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
                    'status': 'success',
                    'message': 'Position order updated successfully',
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