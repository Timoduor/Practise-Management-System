from rest_framework import serializers
from hub.models.sales_task_type import SalesTaskType

class SalesTaskTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesTaskType
        fields = ['id', 'name', 'description']
