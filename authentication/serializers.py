from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=False)
    zip_code = serializers.CharField(required=False)
    avatar = serializers.ImageField(required=False)

    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = get_user_model()
        fields = ('email', 'username', 'first_name', 'last_name', 'phone_number', 
                  'zip_code', 'avatar', 'password')

        def validate_password(self, value):
            if len(value) < 8:
                raise serializers.ValidationError('Password must be at least 8 characters long.')
            return make_password(value)
        
        def create(self, validated_data):
            password = validated_data.pop('password')
            user = super().create(validated_data)
            user.set_password(password)
            user.save()
            return user
