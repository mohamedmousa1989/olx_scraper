from rest_framework import serializers

class OlxQuerySerializer(serializers.Serializer):

    search_keyword = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    size = serializers.IntegerField(required=True, min_value=20)

    def create(self, validated_data):
        """Overridden method."""

    def update(self, instance, validated_data):
        """Overridden method."""