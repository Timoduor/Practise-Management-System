from rest_framework import serializers
from hub.models import Contact, Customer

class ContactSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())

    class Meta:
        model = Contact
        fields = ['contact_id', 'contact_name', 'contact_email', 'contact_phone', 'contact_address', 'contact_role', 'customer', 'is_deleted', 'created_at', 'updated_at']

