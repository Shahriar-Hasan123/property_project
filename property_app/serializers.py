from rest_framework import serializers
from .models import Location


class LocationAutocompleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["id", "name", "city", "state", "country", "slug"]