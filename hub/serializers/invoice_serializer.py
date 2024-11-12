from rest_framework import serializers
from .base_serializer import SoftDeleteBaseSerializer
from hub.models.project import Project
from hub.models.invoice import Invoice
from hub.models.customer import Customer


class InvoiceSerializer(SoftDeleteBaseSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), required=False)
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(), required=False)

    class Meta(SoftDeleteBaseSerializer.Meta):
        model = Invoice
        fields = ['invoice_id', 'project', 'customer', 'invoice_amount', 'invoice_date', 'paid_status', 'entity', 'unit', 'is_deleted', 'created_at', 'updated_at'] + SoftDeleteBaseSerializer.Meta.fields

    def validate(self, data):
        project = data.get('project')
        entity = data.get('entity')
        unit = data.get('unit')

        # Ensure the selected unit belongs to the selected entity
        if unit and entity:
            if unit.entity != entity:
                raise serializers.ValidationError({
                    'unit': 'The selected unit must belong to the selected entity.'
                })

        # Ensure the project belongs to the same entity
        if project and entity:
            if project.entity != entity:
                raise serializers.ValidationError({
                    'entity': 'The invoice must belong to the same entity as the project.'
                })

        # Ensure that the invoice date is valid if both dates are present
        invoice_date = data.get('invoice_date')
        if invoice_date and data.get('created_at') and invoice_date < data.get('created_at').date():
            raise serializers.ValidationError({
                'invoice_date': 'The invoice date cannot be before the creation date.'
            })

        return data
