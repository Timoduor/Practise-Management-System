from rest_framework import serializers
from hub.models.sales_task_status import SalesTaskStatus

class SalesTaskStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesTaskStatus
        fields = ['id', 'name', 'description']
