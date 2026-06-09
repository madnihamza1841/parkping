from rest_framework import serializers
from .models import ChatThread, Message


class MessageSerializer(serializers.ModelSerializer):
    sender_label = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ('uuid', 'sender_label', 'content', 'timestamp', 'is_read', 'is_system')
        read_only_fields = ('uuid', 'sender_label', 'timestamp', 'is_read', 'is_system')

    def get_sender_label(self, obj):
        if obj.is_system:
            return 'System'
        return obj.thread.get_sender_label(obj.sender)


class ChatThreadSerializer(serializers.ModelSerializer):
    car_uuid = serializers.UUIDField(source='car.uuid', read_only=True)
    car_nickname = serializers.CharField(source='car.nickname', read_only=True)
    car_make = serializers.CharField(source='car.make', read_only=True)
    car_model = serializers.CharField(source='car.model', read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatThread
        fields = ('uuid', 'car_uuid', 'car_nickname', 'car_make', 'car_model', 'created_at', 'is_active', 'last_message')

    def get_last_message(self, obj):
        msg = obj.messages.last()
        if msg:
            return {'content': msg.content, 'timestamp': msg.timestamp}
        return None
