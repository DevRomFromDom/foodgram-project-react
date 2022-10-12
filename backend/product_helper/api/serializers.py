from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from product_app.models import (Follow, Ingredient, IngredientAmount, Recipe,
                                Tag, User)
from product_helper.settings import EMAIL_LENGTH, PASSWORD_LENGTH
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator


class BaseUserSerializer(serializers.ModelSerializer):
    """Сериалазер для модели User."""
    is_subscribed = serializers.SerializerMethodField('get_is_subscribed')

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        author_user = User.objects.get(pk=obj.id)
        request_user = self.context.get('request').user
        if author_user != request_user and not request_user.is_anonymous:
            if Follow.objects.filter(
                    user=request_user, author=author_user).exists():
                return True
        return False


class UserSerializer(serializers.ModelSerializer):
    """Сериалазер для модели User."""
    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name', 'last_name', 'password'
        )
        extra_kwargs = {
            'password': {
                'write_only': True,
            },
        }

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class TokenSerializer(serializers.Serializer):
    """Сериалазер без модели, для полей email и password."""
    email = serializers.EmailField(max_length=EMAIL_LENGTH, required=True)
    password = serializers.CharField(
        max_length=PASSWORD_LENGTH, required=True)


class TagSerializer(serializers.ModelSerializer):
    """Сериалазер для модели Tag."""
    class Meta:
        model = Tag
        fields = (
            'id', 'name', 'color', 'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалазер для модели Ingredient."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор модели IngredientAmount."""

    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = IngredientAmount
        fields = (
            'id', 'name', 'measurement_unit', 'amount'
        )

    def get_id(self, obj):
        return obj.ingredient.id

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


class RecipeSerializer(serializers.ModelSerializer):
    """Сериалазер для модели Recipe."""
    tags = TagSerializer(many=True)
    ingredients = IngredientAmountSerializer(many=True)
    image = Base64ImageField(required=True)
    author = serializers.SerializerMethodField('get_author')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients', 'tags',
                  'name', 'image', 'text', 'cooking_time',
                  'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        if not self.context.get('request').user.is_anonymous:
            user = self.context.get('request').user
            return user.favorites.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        if not self.context.get('request').user.is_anonymous:
            user = self.context.get('request').user
            return user.shopping_cart.filter(recipe=obj).exists()
        return False

    def get_author(self, obj):
        instance = get_object_or_404(User, id=obj.author.id)
        serializer = BaseUserSerializer(
            instance, context={'request': self.context.get('request')})
        return serializer.data


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериалазер для создания модели рецептор."""
    tags = serializers.ListField()
    ingredients = serializers.ListField()
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags',
                  'name', 'image', 'text', 'cooking_time')

    def to_representation(self, instance):
        data = RecipeSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        ).data
        return data

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        tags_data = validated_data.pop("tags")
        tags = []
        for tag in tags_data:
            tags.append(Tag.objects.get(pk=tag))
        ingredients = []
        for ing in ingredients_data:
            ingredient, _ = IngredientAmount.objects.get_or_create(
                ingredient=Ingredient.objects.get(pk=ing['id']),
                amount=ing['amount'])
            ingredients.append(ingredient)
        recipe = Recipe.objects.create(
            **validated_data,
            author=get_object_or_404(
                User, username=self.context['request'].user,
            ),
        )
        recipe.tags.set(tags)
        recipe.ingredients.set(ingredients)
        recipe.save()
        return recipe

    def update(self, instance: Recipe, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        tags_data = validated_data.pop("tags")
        tags = []
        for tag in tags_data:
            tags.append(Tag.objects.get(pk=tag))
        ingredients = []
        for ing in ingredients_data:
            new_ingredient, _ = IngredientAmount.objects.get_or_create(
                ingredient=Ingredient.objects.get(
                    pk=ing['id']),
                amount=ing['amount']
            )
            ingredients.append(new_ingredient)

        instance.ingredients.set(ingredients)
        instance.tags.set(tags)
        instance.name = validated_data['name']
        instance.text = validated_data['text']
        instance.cooking_time = validated_data['cooking_time']
        if validated_data.get('image'):
            instance.image = validated_data['image']
        instance.save()
        return instance


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериалазер для избранных рецептов."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class FollowSerializer(BaseUserSerializer):
    recipes_count = serializers.SerializerMethodField('get_recipes_count')
    recipes = serializers.SerializerMethodField('get_recipes')

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed', 'recipes',
                  'recipes_count')

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(pk=obj.id).count()

    def get_recipes(self, obj):
        if self.context['request'].query_params.get('recipes_limit'):
            limit = int(self.context['request'].query_params.get(
                'recipes_limit'))-1
        else:
            limit = None
        serializer = ShortRecipeSerializer(
            obj.recipes.all()[:limit], many=True)
        return serializer.data

    validators = [
        UniqueTogetherValidator(
            queryset=Follow.objects.all(),
            fields=('user', 'author')
        )
    ]