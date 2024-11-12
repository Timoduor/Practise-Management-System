from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from hub.models.sales_type import SalesType
from hub.serializers.sales_type_serializer import SalesTypeSerializer

class SalesTypeViewSet(viewsets.ModelViewSet):
    queryset = SalesType.objects.all()
    serializer_class = SalesTypeSerializer
    permission_classes = [IsAuthenticated]
