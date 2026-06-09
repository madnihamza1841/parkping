from rest_framework import serializers
from .models import Car


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ('uuid', 'plate_number', 'make', 'model', 'variant', 'colour', 'nickname', 'created_at')
        read_only_fields = ('uuid', 'created_at')


class PublicCarSerializer(serializers.ModelSerializer):
    """Returns only non-PII car info for the scan endpoint."""
    class Meta:
        model = Car
        fields = ('uuid', 'nickname', 'make', 'model')
