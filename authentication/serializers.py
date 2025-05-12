from typing import Any
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import AccountSettings


def validate_password(value: Any):
    if len(value) < 8:
        raise serializers.ValidationError(
            'Password must be at least 8 characters long.')
    return make_password(value)


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    zip_code = serializers.CharField(required=False, allow_blank=True)
    avatar = serializers.ImageField(required=False, allow_null=True)
    password = serializers.CharField(
        min_length=8, write_only=True, required=True)
    store = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = get_user_model()
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'phone_number', 'zip_code', 'avatar', 'password', 'store'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = self.Meta.model(**validated_data)
        user.set_password(password)
        user.save()
        return user


class AccountSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountSettings
        fields = ['addr']
