from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend

from core.models.organisation_data import OrganisationData
from core.serializers.organisation_data_serializers import (
    OrganisationDataSerializer,
    OrganisationDataListSerializer,
    OrganisationDataSimpleSerializer
)


class OrganisationDataViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing organisation data
    
    Provides CRUD operations and additional actions for organization data management
    """
    queryset = OrganisationData.objects.all()
    serializer_class = OrganisationDataSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = {
        'instanceID': ['exact'],
        'industrySectorID': ['exact'],
        'Suspended': ['exact'],
        'Lapsed': ['exact'],
        'orgCountry': ['exact', 'icontains'],
        'costCenterEnabled': ['exact'],
        'DateAdded': ['gte', 'lte'],
        'LastUpdate': ['gte', 'lte'],
    }
    
    search_fields = [
        'orgName',
        'orgEmail',
        'orgCity',
        'orgCountry',
        'registrationNumber',
        'orgPIN',
    ]
    
    ordering_fields = [
        'orgName',
        'DateAdded',
        'LastUpdate',
        'orgCity',
        'orgCountry',
        'numberOfEmployees',
    ]
    
    ordering = ['-DateAdded']

    def get_serializer_class(self):
        """Return appropriate serializer class based on the action"""
        if self.action == 'list':
            return OrganisationDataListSerializer
        elif self.action == 'simple_list':
            return OrganisationDataSimpleSerializer
        return OrganisationDataSerializer

    def get_queryset(self):
        """
        Get the list of items for this view.
        Implements filtering by instance, status, and other criteria
        """
        queryset = super().get_queryset()
        
        # Filter by instance
        instance_id = self.request.query_params.get('instance', None)
        if instance_id:
            queryset = queryset.filter(instanceID=instance_id)
            
        # Filter by active status
        active_only = self.request.query_params.get('active_only', False)
        if active_only:
            queryset = queryset.filter(Suspended='NO', Lapsed='NO')
            
        # Filter by industry sector
        industry_sector = self.request.query_params.get('industry_sector', None)
        if industry_sector:
            queryset = queryset.filter(industrySectorID=industry_sector)
            
        # Filter by employee count range
        min_employees = self.request.query_params.get('min_employees', None)
        max_employees = self.request.query_params.get('max_employees', None)
        
        if min_employees:
            queryset = queryset.filter(numberOfEmployees__gte=min_employees)
        if max_employees:
            queryset = queryset.filter(numberOfEmployees__lte=max_employees)
            
        # Search by text query across multiple fields
        search_query = self.request.query_params.get('q', None)
        if search_query:
            queryset = queryset.filter(
                Q(orgName__icontains=search_query) |
                Q(orgEmail__icontains=search_query) |
                Q(orgCity__icontains=search_query) |
                Q(orgCountry__icontains=search_query) |
                Q(registrationNumber__icontains=search_query) |
                Q(orgPIN__icontains=search_query)
            )
            
        return queryset

    def perform_create(self, serializer):
        """Create a new organisation data record with user tracking"""
        serializer.save(LastUpdatedByID=self.request.user)

    def perform_update(self, serializer):
        """Update an organisation data record with user tracking"""
        serializer.save(LastUpdatedByID=self.request.user)

    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        """Suspend an organisation"""
        org_data = self.get_object()
        org_data.Suspended = 'YES'
        org_data.save(update_fields=['Suspended', 'LastUpdate'])
        
        serializer = self.get_serializer(org_data)
        return Response({
            'status': 'success',
            'message': f'Organisation {org_data.orgName} has been suspended',
            'data': serializer.data
        })

    @action(detail=True, methods=['post'])
    def unsuspend(self, request, pk=None):
        """Unsuspend an organisation"""
        org_data = self.get_object()
        org_data.Suspended = 'NO'
        org_data.save(update_fields=['Suspended', 'LastUpdate'])
        
        serializer = self.get_serializer(org_data)
        return Response({
            'status': 'success',
            'message': f'Organisation {org_data.orgName} has been unsuspended',
            'data': serializer.data
        })

    @action(detail=True, methods=['post'])
    def lapse(self, request, pk=None):
        """Mark organisation as lapsed"""
        org_data = self.get_object()
        org_data.Lapsed = 'YES'
        org_data.save(update_fields=['Lapsed', 'LastUpdate'])
        
        serializer = self.get_serializer(org_data)
        return Response({
            'status': 'success',
            'message': f'Organisation {org_data.orgName} has been marked as lapsed',
            'data': serializer.data
        })

    @action(detail=True, methods=['post'])
    def unlapse(self, request, pk=None):
        """Remove lapsed status"""
        org_data = self.get_object()
        org_data.Lapsed = 'NO'
        org_data.save(update_fields=['Lapsed', 'LastUpdate'])
        
        serializer = self.get_serializer(org_data)
        return Response({
            'status': 'success',
            'message': f'Organisation {org_data.orgName} is no longer marked as lapsed',
            'data': serializer.data
        })
        
    @action(detail=False)
    def statistics(self, request):
        """Get statistics about organisations"""
        queryset = self.get_queryset()
        
        # Count by status
        suspended_count = queryset.filter(Suspended='YES').count()
        lapsed_count = queryset.filter(Lapsed='YES').count()
        active_count = queryset.filter(Suspended='NO', Lapsed='NO').count()
        total_count = queryset.count()
        
        # Count by industry sector
        industry_breakdown = {}
        for org in queryset:
            sector_name = str(org.industrySectorID)
            if sector_name in industry_breakdown:
                industry_breakdown[sector_name] += 1
            else:
                industry_breakdown[sector_name] = 1
        
        # Count by country
        country_breakdown = {}
        for org in queryset:
            country = org.orgCountry
            if country in country_breakdown:
                country_breakdown[country] += 1
            else:
                country_breakdown[country] = 1
                
        stats = {
            'total_organisations': total_count,
            'active_organisations': active_count,
            'suspended_organisations': suspended_count,
            'lapsed_organisations': lapsed_count,
            'by_industry': industry_breakdown,
            'by_country': country_breakdown,
        }
        
        return Response(stats)

    @action(detail=False)
    def simple_list(self, request):
        """Get simplified list of organisations"""
        queryset = self.get_queryset()
        serializer = OrganisationDataSimpleSerializer(queryset, many=True)
        return Response(serializer.data)
        
    @action(detail=True)
    def related_entities(self, request, pk=None):
        """Get entities related to this organisation data"""
        org_data = self.get_object()
        
        # Get related entities through organisation charts
        related_charts = org_data.organisation_chart.all() if hasattr(org_data, 'organisation_chart') else []
        
        entities = []
        for chart in related_charts:
            entity = chart.entityID
            entities.append({
                'id': entity.id,
                'name': entity.entityName if hasattr(entity, 'entityName') else str(entity),
                'chart_id': chart.orgChartID,
                'chart_name': chart.orgChartName,
            })
            
        return Response({
            'count': len(entities),
            'entities': entities
        })

    @action(detail=True)
    def organisation_charts(self, request, pk=None):
        """Get organisation charts for this organisation data"""
        org_data = self.get_object()
        
        # Get related organisation chart
        chart = getattr(org_data, 'organisation_chart', None)
        
        if chart:
            from core.serializers.organisation_chart_serializers import OrganisationChartSerializer
            serializer = OrganisationChartSerializer(chart)
            return Response(serializer.data)
        
        return Response({'message': 'No organisation chart found'}, status=status.HTTP_404_NOT_FOUND)