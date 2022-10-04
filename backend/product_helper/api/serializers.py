from product_app.models import User, Tag
from product_helper.settings import EMAIL_LENGTH, PASSWORD_LENGTH
from rest_framework import serializers


class BaseUserSerializer(serializers.ModelSerializer):
    """Сериалазер для модели User."""
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',  'first_name', 'last_name'
        )


class UserSerializer(serializers.ModelSerializer):
    """Сериалазер для модели User."""
    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name', 'last_name', 'password'
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериалазер для модели Tag."""
    class Meta:
        model = Tag
        fields = (
            'id', 'name', 'color', 'slug',
        )


class TokenSerializer(serializers.Serializer):
    """Сериалазер без модели, для полей email и password."""
    email = serializers.EmailField(max_length=EMAIL_LENGTH, required=True)
    password = serializers.CharField(
        max_length=PASSWORD_LENGTH, required=True)
