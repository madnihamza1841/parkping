from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('email', 'password', 'full_name', 'date_of_birth', 'phone_number')
        extra_kwargs = {
            'date_of_birth': {'required': False},
            'phone_number': {'required': False},
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def to_representation(self, instance):
        return {'id': instance.pk, 'email': instance.email, 'full_name': instance.full_name}


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'full_name', 'avatar', 'created_at')
        read_only_fields = ('id', 'email', 'created_at')


class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('avatar',)
