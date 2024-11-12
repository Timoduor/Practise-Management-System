from rest_framework import serializers
from .base_serializer import SoftDeleteBaseSerializer
from hub.models.contact import Contact
from hub.models.customer import Customer


class ContactSerializer(SoftDeleteBaseSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())

    class Meta(SoftDeleteBaseSerializer.Meta):
        model = Contact
        fields = ['contact_id', 'contact_name', 'contact_email', 'contact_phone', 'contact_address', 'contact_role', 'customer', 'is_deleted', 'created_at', 'updated_at'] + SoftDeleteBaseSerializer.Meta.fields

