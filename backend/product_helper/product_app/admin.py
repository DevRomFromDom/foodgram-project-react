from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientAmount, Recipe,
                     ShoppingCart, Tag, User)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', )
    search_fields = ('username', 'email')
    list_filter = ('username', 'email')
    empty_value_display = '-пусто-'


@admin.register(IngredientAmount)
class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'amount',)
    search_fields = ('amount', )
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorites_count')
    search_fields = ('name', 'author__username', 'ingredients')
    list_filter = ('tags', 'name', 'author')
    empty_value_display = '-пусто-'

    @admin.display(description='Всего в избранных')
    def favorites_count(self, obj):
        return obj.favorites.all().count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    prepopulated_fields = {"slug": ("name",)}
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name', )
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    fields = ('recipe',)
    list_display = ('user',)
    search_fields = ('user', )
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    fields = ('recipe',)
    list_display = ('user',)
    search_fields = ('user', )
    empty_value_display = '-пусто-'
