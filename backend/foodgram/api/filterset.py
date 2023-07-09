from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from recipes.models import Ingredient, Recipe


# class IngredientFilter(FilterSet):
#     """Поиск ингредиентов по имени."""
#     name = filters.CharFilter(lookup_expr="istartswith")

#     class Meta:
#         model = Ingredient
#         fields = ("name",)

class IngredientSearchFilter(SearchFilter):
    """Поиск ингредиентов по имени."""

    search_param = 'name'


class RecipeFilter(FilterSet):
    is_favorited = filters.BooleanFilter(method='get_is_favorited',)
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart',
    )
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
    )

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')

    def get_is_favorited(self, queryset, is_favorited, slug):
        user = self.request.user
        if not user.is_authenticated:
            return queryset
        is_favorited = self.request.query_params.get('is_favorited',)
        if is_favorited:
            return queryset.filter(
                favorites__user=self.request.user
            ).distinct()
        return queryset

    def get_is_in_shopping_cart(self, queryset, is_in_shopping_cart, slug):
        user = self.request.user
        if not user.is_authenticated:
            return queryset
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart',
        )
        if is_in_shopping_cart:
            return queryset.filter(
                shopping_cart__user=self.request.user
            ).distinct()
        return queryset
