from rest_framework import serializers
from hub.models.sales_status import SalesStatus

class SalesStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesStatus
        fields = ['id', 'name', 'description']
