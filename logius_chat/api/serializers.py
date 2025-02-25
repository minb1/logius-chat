from rest_framework import serializers

class ChatRequestSerializer(serializers.Serializer):
    """
    Serializer for chat request data.
    """
    query = serializers.CharField(required=True)

class ChatResponseSerializer(serializers.Serializer):
    """
    Serializer for chat response data.
    """
    response = serializers.CharField()
