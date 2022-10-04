from django.contrib import admin

from .models import User, Recipe, Tag, Ingredient


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', )
    search_fields = ('username',)
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author',)
    search_fields = ('name', 'author', )
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    prepopulated_fields = {"slug": ("name",)}
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name', )
    empty_value_display = '-пусто-'
