from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models

from .validators import hex_color_validator, username_validator


class User(AbstractUser):
    """Модель пользователя."""
    username = models.CharField(
        'Имя пользователя',
        unique=True,
        max_length=settings.USERNAME_LENGTH,
        validators=(username_validator,)
    )
    email = models.EmailField(
        'Email пользователя',
        blank=False,
        unique=True,
        max_length=settings.EMAIL_LENGTH,
    )
    first_name = models.CharField(
        'Имя',
        max_length=settings.FIRST_NAME_LENGTH,
        blank=False,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=settings.LAST_NAME_LENGTH,
        blank=False,
    )
    password = models.CharField(
        'Пароль',
        max_length=settings.PASSWORD_LENGTH,
        blank=False
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
        blank=False)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
        blank=False
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow')
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'


class Tag(models.Model):
    """Тег для рецепта."""
    name = models.CharField(
        'Название тэга',
        blank=False,
        max_length=settings.TAG_NAME_LENGTH,
        help_text='Название тэга',
        unique=True
    )
    color = models.CharField(
        'Цвет тега',
        max_length=7,
        unique=True,
        validators=(hex_color_validator,)
    )
    slug = models.SlugField(
        unique=True,
        max_length=200,
        verbose_name='Метка URL',
        blank=False,
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ингридиент."""
    name = models.CharField(
        'Название ингридиента',
        blank=False,
        max_length=settings.INGRIDIENT_NAME_LENGTH,
        help_text='Название ингридиента'
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        blank=False,
        max_length=settings.MEASURMENT_COUNT_LENGTH,
        help_text='Единица измерения'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    """Модель количества ингредиента."""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_amount',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        blank=False,
        validators=(
            validators.MinValueValidator(
                1, message='Минимальное количество ингридиентов 1'
            ), validators.MaxValueValidator(
                10000,
                message='Максимальное количество ингридиентов 10000')
        ),
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'

    def __str__(self):
        return (f'{self.ingredient.name} ({self.ingredient.measurement_unit})'
                f' - {self.amount}')


class Recipe(models.Model):
    """Модель рецепта."""
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        'Название рецепта',
        blank=False,
        max_length=settings.RECIPE_NAME_LENGTH,
        help_text='Название рецепта'
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Картинка к рецепту',
        blank=False,
    )
    text = models.TextField(
        'Описание',
        max_length=settings.RECIPE_DESC_LENGTH,
        blank=False,
        help_text='Описание рецепта'
    )
    ingredients = models.ManyToManyField(
        IngredientAmount,
        related_name='ingredients',
        verbose_name='Ингридиенты для рецепта',
        blank=False,
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='tags',
        verbose_name='Tэг рецепта',
        blank=False
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        blank=False,
        validators=(
            validators.MinValueValidator(
                1, message='Минимальное время приготовления 1 минута'
            ), validators.MaxValueValidator(
                10000,
                message='Максимальное количество ингридиентов 10000')
        ),
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Favorite(models.Model):
    """Избранные рецепты."""
    user = models.ForeignKey(
        User,
        related_name='favorites',
        on_delete=models.CASCADE
    )
    recipe = models.ManyToManyField(
        Recipe,
        related_name='favorites',
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'


class ShoppingCart(models.Model):
    """Список покупок."""
    user = models.ForeignKey(
        User,
        related_name='shopping_cart',
        on_delete=models.CASCADE
    )
    recipe = models.ManyToManyField(
        Recipe,
        related_name='shopping_cart',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
