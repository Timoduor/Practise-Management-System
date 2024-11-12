from hub.models.leave_type import LeaveType
from .base_serializer import SoftDeleteBaseSerializer

class LeaveTypeSerializer(SoftDeleteBaseSerializer):
    class Meta(SoftDeleteBaseSerializer.Meta):
        model = LeaveType
        fields = ['id', 'name', 'description', 'is_paid', 'created_at', 'updated_at'] + SoftDeleteBaseSerializer.Meta.fields

