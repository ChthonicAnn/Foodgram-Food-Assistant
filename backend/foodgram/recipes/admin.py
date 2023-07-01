from django.contrib import admin

from .models import (
    Favorite, Ingredient, IngredientInRecipe,
    Recipe, ShoppingCart, Tag
)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'id',)
    list_filter = ('name', 'author', 'tags',)
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'id',)
    list_filter = ('name',)
    search_fields = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'slug',)
    list_filter = ('name',)


admin.site.register(Favorite)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientInRecipe)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShoppingCart)
admin.site.register(Tag, TagAdmin)
