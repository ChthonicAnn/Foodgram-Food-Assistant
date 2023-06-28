from django.contrib.auth import get_user_model
# from django.contrib.auth.tokens import default_token_generator
# from django.contrib.sites.shortcuts import get_current_site
from django.db.models import F, Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filterset import RecipeFilter
from .paginators import CustomPagination
from .permissions import IsAdminOrReadOnly, IsAdminOrAuthorOrReadOnly
from recipes.models import (
    Favorite, Ingredient, IngredientInRecipe,
    Recipe, ShoppingCart, Tag
)

from .serializers import (
    FavoriteSerializer, IngredientShowSerializer,
    RecipeCreateSerializer, RecipeShowSerializer,
    ShoppingCartSerializer, TagSerializer
)

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPagination
    permission_classes = IsAdminOrAuthorOrReadOnly

    def get_serializer_class(self):
        if self.action in (['retrieve', 'list']):
            return RecipeShowSerializer
        return RecipeCreateSerializer

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = False
        return self.update(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def post_delete_fav_shop_cart(self, request, pk, model, serializer):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        author = get_object_or_404(User, pk=pk)

        if self.request.method == 'POST':
            model_create = model.objects.filter(user=user, recipe=recipe)
            if not model_create.exists():
                if request.user != author:
                    model.objects.create(
                        author=request.user,
                        recipe=recipe
                    )
                    serializer = serializer()
                    return Response(serializer.data)
            raise Response(status=status.HTTP_204_NO_CONTENT)

        if self.request.method == 'DELETE':
            model_delete = model.objects.filter(user=user, recipe=recipe)
            if model_delete.exists():
                model_delete.delete()
            raise Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=('post', 'delete'), url_path='favorite',
            permission_classes=[IsAuthenticated],)
    def favorite(self, request, pk=None):
        return self.post_delete_fav_shop_cart(
            request, pk, Favorite, FavoriteSerializer)

    @action(detail=True, methods=('post', 'delete'), url_path='shopping_cart',
            permission_classes=[IsAuthenticated],)
    def shopping_cart(self, request, pk=None):
        return self.post_delete_fav_shop_cart(
            request, pk, ShoppingCart, ShoppingCartSerializer)

    @action(detail=False, methods=('get',),
            permission_classes=[IsAuthenticated],)
    def download_shopping_cart(self, request):
        user = request.user

        if not user.shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_cart__user=user).values_list(
            'ingredient__name', 'ingredient__measurement_unit').annotate(
            name=F('ingredient__name'),
            unit=F('ingredient__measurement_unit'),
            total_amount=Sum('amount')
            ).order_by('-total_amount')

        shopping_list = '\r\n'.join(
            [(f"{ing['name']}: {ing['total_amount']} {ing['unit']} ")
             for ing in ingredients]
            )
        response = HttpResponse(shopping_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингридиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientShowSerializer
    filter_backends = (filters.SearchFilter)
    search_fields = ('^name',)
    permission_classes = (IsAdminOrReadOnly,)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
