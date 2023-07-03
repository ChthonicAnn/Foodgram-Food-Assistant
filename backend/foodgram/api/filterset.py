from django_filters import rest_framework

from recipes.models import Recipe


class RecipeFilter(rest_framework.FilterSet):
    is_favorited = rest_framework.BooleanFilter(method='get_favorite',)
    is_in_shopping_cart = rest_framework.BooleanFilter(
        method='get_is_in_shopping_cart',
    )
    tags = rest_framework.AllValuesMultipleFilter(
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
                favorites__user=self.request.user
            ).distinct()
        return queryset

    def get_is_in_shopping_cart(self, queryset, is_in_shopping_cart):
        user = self.request.user
        if not user.is_authenticated:
            return queryset
        if is_in_shopping_cart:
            return queryset.filter(
                favorites__user=self.request.user
            ).distinct()
        return queryset
