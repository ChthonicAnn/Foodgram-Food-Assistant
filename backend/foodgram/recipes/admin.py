from django.contrib import admin

from .models import Favorites, Ingredients, Recipes, IngredientsInRecipe, Tag

admin.site.register(Favorites)
admin.site.register(Ingredients)
admin.site.register(Recipes)
admin.site.register(IngredientsInRecipe)
admin.site.register(Tag)
