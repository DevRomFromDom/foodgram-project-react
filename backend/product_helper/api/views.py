from django.shortcuts import get_object_or_404
from djoser import views
from product_app.models import Ingredient, Recipe, Tag, User
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (BaseUserSerializer, TagSerializer, TokenSerializer,
                          UserSerializer)


class CustomUserView(views.UserViewSet):
    def get_serializer_class(self):
        if self.action == 'create':
            return UserSerializer
        elif self.action in ['list', 'me', 'retrieve']:
            return BaseUserSerializer
        else:
            return super().get_serializer_class()


@api_view(['POST'])
def create_token(request):
    """Создание токена."""
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(User, email=serializer.data['email'])
    token = RefreshToken.for_user(user)
    return Response(
        {"auth_token": f"{token.access_token}"},
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
def delete_token(request):
    """Удаление токена."""
    if request.user.is_anonymous:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    return Response(
        status=status.HTTP_204_NO_CONTENT
    )


class TagListRetrieveViewSet(mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             viewsets.GenericViewSet
                             ):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get_paginated_response(self, data):
        return Response(data)
