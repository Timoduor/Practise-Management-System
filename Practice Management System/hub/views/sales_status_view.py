from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from hub.models.sales_status import SalesStatus
from hub.serializers.sales_status_serializer import SalesStatusSerializer

class SalesStatusViewSet(viewsets.ModelViewSet):
    queryset = SalesStatus.objects.all()
    serializer_class = SalesStatusSerializer
    permission_classes = [IsAuthenticated]
    # Same logic: all authenticated users have full access
