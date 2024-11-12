from rest_framework import serializers
from hub.models.sales_type import SalesType

class SalesTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesType
        fields = ['id', 'name', 'description']
