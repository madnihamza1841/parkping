from django.utils import timezone
from rest_framework import serializers
from .models import ChatThread, Message, Block, CHAT_EXPIRY


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
    expires_at = serializers.SerializerMethodField()
    blocked_by_me = serializers.SerializerMethodField()
    is_blocked = serializers.SerializerMethodField()

    class Meta:
        model = ChatThread
        fields = ('uuid', 'car_uuid', 'car_nickname', 'car_make', 'car_model',
                  'created_at', 'is_active', 'last_message', 'expires_at',
                  'blocked_by_me', 'is_blocked')

    def get_last_message(self, obj):
        cutoff = timezone.now() - CHAT_EXPIRY
        msg = obj.messages.filter(timestamp__gte=cutoff).last()
        if msg:
            return {'content': msg.content, 'timestamp': msg.timestamp}
        return None

    def get_expires_at(self, obj):
        return obj.expires_at

    def _request_user(self):
        request = self.context.get('request')
        return request.user if request else None

    def get_blocked_by_me(self, obj):
        """True if the requesting user has blocked the other participant."""
        user = self._request_user()
        if not user:
            return False
        return Block.objects.filter(blocker=user, blocked=obj.other_participant(user)).exists()

    def get_is_blocked(self, obj):
        """True if a block exists in either direction — chat/calls disabled."""
        user = self._request_user()
        if not user:
            return False
        return Block.exists_between(user, obj.other_participant(user))
