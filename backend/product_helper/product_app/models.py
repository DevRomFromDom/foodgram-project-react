from django.core import validators
from django.contrib.auth.models import AbstractUser
from django.db import models
from product_helper.settings import (
    EMAIL_LENGTH, FIRST_NAME_LENGTH,
    LAST_NAME_LENGTH, PASSWORD_LENGTH,
    RECIPE_DESC_LENGTH, TAG_NAME_LENGTH, RECIPE_NAME_LENGTH,
    INGRIDIENT_NAME_LENGTH, MEASURMENT_COUNT_LENGTH,
    USERNAME_LENGTH
)
from .validators import username_validator, slug_validator


class User(AbstractUser):
    """Модель пользователя."""
    username = models.CharField(
        'Имя пользователя',
        unique=True,
        max_length=USERNAME_LENGTH,
        blank=False,
        validators=[username_validator]
    )
    email = models.EmailField(
        'Email пользователя',
        blank=False,
        unique=True,
        max_length=EMAIL_LENGTH,
    )
    first_name = models.CharField(
        'Имя',
        max_length=FIRST_NAME_LENGTH,
        blank=False,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=LAST_NAME_LENGTH,
        blank=False,
    )
    password = models.CharField(
        'Пароль',
        max_length=PASSWORD_LENGTH,
        blank=False
    )

    class Meta:
        ordering = ['username']
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
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name="unique_follow")
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'


class Tag(models.Model):
    """Тег для рецепта."""
    name = models.CharField(
        'Название тэга',
        blank=False,
        max_length=TAG_NAME_LENGTH,
        help_text='Название тэга'
    )
    color = models.CharField(
        'Цвет тега',
        blank=True,
        max_length=7
    )
    slug = models.SlugField(
        unique=True,
        max_length=200,
        verbose_name='Метка URL',
        blank=False,
        validators=[slug_validator]
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ингридиент."""
    name = models.CharField(
        'Название ингридиента',
        blank=False,
        max_length=INGRIDIENT_NAME_LENGTH,
        help_text='Название ингридиента'
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        blank=False,
        max_length=MEASURMENT_COUNT_LENGTH,
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
                1, message="Минимальное количество ингридиентов 1"
            ),
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
        verbose_name="Автор рецепта",
    )
    name = models.CharField(
        'Название рецепта',
        blank=False,
        max_length=RECIPE_NAME_LENGTH,
        help_text='Название рецепта'
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Картинка к рецепту',
        blank=False,
    )
    text = models.TextField(
        'Описание',
        max_length=RECIPE_DESC_LENGTH,
        blank=False,
        help_text="Описание рецепта"
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
                1, message="Минимальное время приготовления 1 минута"
            ),
        ),
    )
    pub_date = models.DateTimeField(
        "Дата публикации",
        auto_now_add=True
    )

    class Meta:
        ordering = ("-pub_date",)
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
    """Список пакупок."""
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
        verbose_name = 'Список пакупок'
        verbose_name_plural = 'Списки покупок'
