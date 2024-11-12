from datetime import datetime
from rest_framework import serializers
from .base_serializer import SoftDeleteBaseSerializer
from hub.models.absence import Absence
from hub.models.project import Project
from hub.models.leave_type import LeaveType
from hub.models.sales import Sales


class AbsenceSerializer(SoftDeleteBaseSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), required=False)
    sale = serializers.PrimaryKeyRelatedField(queryset=Sales.objects.all(), required=False, allow_null=True)

    leave_type = serializers.PrimaryKeyRelatedField(queryset=LeaveType.objects.all(), required=False)

    class Meta(SoftDeleteBaseSerializer.Meta):
        model = Absence
        fields = ['absence_id', 'user', 'absence_date', 'start_time', 'end_time','duration' ,'absence_description', 'project','sale' ,'leave_type', 'is_deleted', 'created_at', 'updated_at'] + SoftDeleteBaseSerializer.Meta.fields
        extra_kwargs = {
            'project': {'required': False, 'allow_null': True},    
            'sale': {'required': False, 'allow_null': True},

        }

    def validate(self, data):
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        if start_time and end_time and start_time > end_time:
            raise serializers.ValidationError("End time must be after the start time.")

        return data

    def create(self, validated_data):
        # Calculate the duration and save it in the database
        start_time = validated_data.get('start_time')
        end_time = validated_data.get('end_time')

        
        today = datetime.today().date()  # Common date for both times

        # Combine date and time into datetime objects
        start_datetime = datetime.combine(today, start_time)
        end_datetime = datetime.combine(today, end_time)

        # Calculate the difference (this will be a timedelta object)
        validated_data["duration"] = end_datetime - start_datetime
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Calculate the duration when updating as well
        start_time = validated_data.get('start_time', instance.start_time)
        end_time = validated_data.get('end_time', instance.end_time)
        today = datetime.today().date()  # Common date for both times

        # Combine date and time into datetime objects
        start_datetime = datetime.combine(today, start_time)
        end_datetime = datetime.combine(today, end_time)

        # Calculate the difference (this will be a timedelta object)
        instance.duration = end_datetime - start_datetime
        return super().update(instance, validated_data)

