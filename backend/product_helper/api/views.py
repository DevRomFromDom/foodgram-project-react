from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from product_app.models import (Favorite, Follow, Ingredient, IngredientAmount,
                                Recipe, ShoppingCart, Tag, User)
from rest_framework import mixins, permissions, status, views, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .permissions import OwnerOrReadOnly
from .serializers import (BaseUserSerializer, CreateRecipeSerializer,
                          FollowSerializer, IngredientSerializer,
                          RecipeSerializer, ShortRecipeSerializer,
                          TagSerializer, TokenSerializer, UserSerializer)


class CustomUserView(UserViewSet):
    """Кастомный вьюсет Djoser."""

    def get_serializer_class(self):
        """Получение сериализаторов для определенных событий."""
        if self.action == 'create':
            return UserSerializer
        elif self.action in ['list', 'me', 'retrieve']:
            return BaseUserSerializer
        elif self.action == 'set_password':
            return super().get_serializer_class()
        return super().get_serializer_class(
            context={
                'request': self.request})

    def get_permissions(self):
        """Предоставление прав для определенных событий."""
        if self.action in ['retrieve', "user_list"]:
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def create_token(request):
    """Создание токена."""
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        user = User.objects.get(email=serializer.data['email'])
        if not check_password(serializer.data['password'], user.password):
            return Response(
                {"Данные авторизации предоставлены не верно."},
                status=status.HTTP_400_BAD_REQUEST)
        token = RefreshToken.for_user(user)
        return Response(
            {"auth_token": f"{token.access_token}"},
            status=status.HTTP_201_CREATED
        )
    except ObjectDoesNotExist:
        return Response(
            {"Пользователя с данным email не существует."},
            status=status.HTTP_400_BAD_REQUEST)


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
    """Вьюсет для тэгов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get_paginated_response(self, data):
        """Возвращение данных без пагинации."""
        return Response(data)


class IngredientsListRetrieveView(mixins.ListModelMixin,
                                  mixins.RetrieveModelMixin,
                                  viewsets.GenericViewSet
                                  ):
    """Вьюсет для ингридиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    def get_paginated_response(self, data):
        """Возвращение данных без пагинации."""
        return Response(data)


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""
    page_size_query_param = 'limit'
    permission_classes = [OwnerOrReadOnly]

    def get_queryset(self):
        """Формирование списка рецептов в зависимости от query параметров."""
        recipes = Recipe.objects.all()
        tags_query = self.request.query_params.getlist('tags')
        author = self.request.query_params.get('author')
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )

        if is_favorited == '1':
            recipes = recipes.filter(
                favorites__in=Favorite.objects.filter(
                    user=self.request.user
                )
            )
        if is_in_shopping_cart == '1':
            recipes = recipes.filter(
                shopping_cart__in=ShoppingCart.objects.filter(
                    user=self.request.user
                )
            )
        if author:
            recipes = recipes.filter(author__id=int(author))
        if tags_query:
            recipes = recipes.exclude(
                tags__in=Tag.objects.exclude(slug__in=tags_query))
        return recipes or Recipe.objects.none()

    def get_serializer_class(self):
        """Получение сериализатора для конкретного события."""
        if self.action in ['list', 'retrieve']:
            return RecipeSerializer
        elif self.action in ['create', 'update']:
            return CreateRecipeSerializer
        return super().get_serializer_class(context={
            'request': self.request})

    def list(self, request):
        """Получение списка рецептов."""
        serializer = self.get_serializer(self.get_queryset(), many=True)
        page = self.paginate_queryset(self.get_queryset())
        if page is not None:
            serialize_page = self.get_serializer(page, many=True)
            return self.get_paginated_response(serialize_page.data)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Получение рецепта по ID."""
        recipe = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(recipe)
        return Response(serializer.data)

    def create(self, request):
        """Создание рецепта."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk, *args, **kwargs):
        """Изменение рецепта."""
        partial = kwargs.pop('partial', False)
        instance = get_object_or_404(Recipe, pk=pk)
        serializer = CreateRecipeSerializer(
            instance, data=request.data, partial=partial, context={
                'request': self.request})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """Частичное изменение рецепта."""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, pk):
        """Удаление рецепта."""
        instanse = get_object_or_404(Recipe, pk=pk)
        self.perform_destroy(instance=instanse)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteCreateDestroyView(views.APIView):
    """Вью для избранных рецептов."""

    def post(self, request, id=None):
        """Добавление рецепта в список избранного."""
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=id)

        try:
            Favorite.objects.get(user=user, recipe=recipe)
            return Response(
                {'error': 'Этот рецепт уже в вашем списке покупок.', },
                status=status.HTTP_400_BAD_REQUEST
            )
        except ObjectDoesNotExist:
            instace, _ = Favorite.objects.get_or_create(user=user)
            instace.recipe.add(recipe)

            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        """Удаление рецепта из избранного."""
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=id)

        try:
            favorite = Favorite.objects.get(user=user, recipe=recipe)
            favorite.recipe.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response(
                {'error': 'Этого рецепта нет в вашем списке покупок.', },
                status=status.HTTP_400_BAD_REQUEST
            )


class ShoppingCartCreateDestroyView(views.APIView):
    """Вью для рецептов корзины."""

    def get(self, request):
        """Создание и отправка списка покупок."""
        user = self.request.user
        shopping_cart = ShoppingCart.objects.filter(user=user)[0]
        recipes = Recipe.objects.filter(shopping_cart__id=shopping_cart.id)
        shopping_cart = {}
        ingredients = IngredientAmount.objects.filter(
            ingredients__in=recipes
        )
        for ingredient in ingredients:
            key = (f'{ingredient.ingredient.name} '
                   f'({ingredient.ingredient.measurement_unit}) —')
            try:
                shopping_cart[key] += ingredient.amount
            except KeyError:
                shopping_cart[key] = ingredient.amount
        with open('shopping_cart.txt', "w") as file:
            for name, amount in shopping_cart.items():
                file.write(f'{name} {amount}' + '\n')
        short_report = open("shopping_cart.txt", 'r')
        return HttpResponse(short_report, content_type='text/plain')

    def post(self, request, id=None):
        """Добавление рецепта в корзину."""
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=id)

        try:
            ShoppingCart.objects.get(user=user, recipe=recipe)
            return Response(
                {'error': 'Этот рецепт уже в вашем списке покупок.', },
                status=status.HTTP_400_BAD_REQUEST
            )
        except ObjectDoesNotExist:
            instace, _ = ShoppingCart.objects.get_or_create(user=user)
            instace.recipe.add(recipe)

            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        """Удаление рецепта из корзины."""
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=id)

        try:
            shopping_cart_recipe = ShoppingCart.objects.get(
                user=user, recipe=recipe)
            shopping_cart_recipe.recipe.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response(
                {'error': 'Этого рецепта нет в вашем списке покупок.', },
                status=status.HTTP_400_BAD_REQUEST
            )


class FollowListViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов подписок."""
    page_size_query_param = 'limit'

    def get_queryset(self):
        """Получение всех авторов на которых подписан пользватель."""
        user = self.request.user
        if user.follower.all().exists():
            followers_ids = list(
                user.follower.all().values_list('author')[0])
            queryset = User.objects.filter(id__in=followers_ids)
        return queryset or User.objects.none()

    def list(self, request):
        """
        Получение списка всех авторов
        на которых подписан пользователь
        и их рецепты.
        """
        serializer = FollowSerializer(self.get_queryset(), many=True, context={
            'request': self.request})
        page = self.paginate_queryset(self.get_queryset())
        if page is not None:
            serialize_page = FollowSerializer(page, many=True, context={
                'request': self.request})
            return self.get_paginated_response(serialize_page.data)
        return Response(serializer.data)


class FollowView(views.APIView):
    """Вью для подписок."""

    def post(self, request, id):
        """Подписаться на автора."""
        author_follow = get_object_or_404(User, pk=id)
        user = request.user
        if (author_follow == user or Follow.objects.filter(
                author=author_follow, user=user).exists()):
            return Response({'error': 'Вы уже подписаны'
                             'на автора или вы и есть автор.', },
                            status=status.HTTP_400_BAD_REQUEST)
        Follow.objects.get_or_create(author=author_follow, user=user)
        serializer = FollowSerializer(author_follow, context={
            'request': self.request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        """Отписаться от автора."""
        author_unfollow = get_object_or_404(User, pk=id)
        user = request.user
        if Follow.objects.filter(author=author_unfollow, user=user).exists():
            follow = Follow.objects.filter(author=author_unfollow, user=user)
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Такой подписки не существует.', },
                        status=status.HTTP_400_BAD_REQUEST)
