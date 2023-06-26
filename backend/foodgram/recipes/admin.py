from django.contrib import admin

from .models import (
    Favorite, Ingredient, IngredientInRecipe,
    Recipe, ShoppingCart, Tag
)


class PostAdmin(admin.ModelAdmin):
    # Перечисляем поля, которые должны отображаться в админке
    list_display = ('pk', 'text', 'pub_date', 'author')
    # Добавляем интерфейс для поиска по тексту постов
    search_fields = ('text',)
    # Добавляем возможность фильтрации по дате
    list_filter = ('pub_date',)
    # Это свойство сработает для всех колонок: где пусто — там будет эта строка
    empty_value_display = '-пусто-'


admin.site.register(Favorite)
admin.site.register(Ingredient)
admin.site.register(IngredientInRecipe)
admin.site.register(Recipe)
admin.site.register(ShoppingCart)
admin.site.register(Tag)
