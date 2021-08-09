from rest_framework import serializers


class CustomSerializer(serializers.Serializer):

    def to_representation(self, instance):
        # Support lazy objects
        return super().to_representation(instance() if callable(instance) else instance)
