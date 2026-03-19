from rest_framework import serializers

class SoftDeleteBaseSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    last_updated_by = serializers.PrimaryKeyRelatedField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        validated_data['last_updated_by'] = self.context['request'].user
        return super().create(validated_data)
    

    def update(self, instance, validated_data):
        validated_data['last_updated_by'] = self.context['request'].user
        return super().update(instance,validated_data)
    
    class Meta:
        abstract = True
        fields =['created_by', 'last_updated_by', 'created_at', 'updated_at']

