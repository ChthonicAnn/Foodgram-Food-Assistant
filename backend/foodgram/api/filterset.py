from django_filters.rest_framework import FilterSet, filters

from recipes.models import Recipe  # Ingredient

# class IngredientFilter(FilterSet):
#     """Поиск ингредиентов по имени."""

#     search_param = 'name'
    # name = filters.CharFilter(lookup_expr="istartswith")

    # class Meta:
    #     model = Ingredient
    #     fields = ("name",)


class RecipeFilter(FilterSet):
    is_favorited = filters.BooleanFilter(method='get_favorite',)
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart',
    )
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
    )

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')

    def get_favorite(self, queryset, is_favorited):
        user = self.request.user
        if not user.is_authenticated:
            return queryset
        if is_favorited:
            return queryset.filter(
                favorite_recipe__user=self.request.user
            ).distinct()
        return queryset

    def get_is_in_shopping_cart(self, queryset, is_in_shopping_cart):
        user = self.request.user
        if not user.is_authenticated:
            return queryset
        if is_in_shopping_cart:
            return queryset.filter(
                shopping_cart_recipe__user=self.request.user
            ).distinct()
        return queryset
