import base64

from django.contrib.auth import get_user_model
# from django.contrib.auth.models import User
from django.core.files.base import ContentFile
# from django.shortcuts import get_object_or_404
from django.core.validators import MinValueValidator
from rest_framework import serializers
# from rest_framework.validators import UniqueTogetherValidator
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from recipes.models import (
    Favorite, Ingredient, IngredientInRecipe,
    Recipe, ShoppingCart, Tag
)
from users.models import Subscriptions
from users.serializers import CustomUserSerializer

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Кодирует картинку в строку base64."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тег."""
    color = serializers.CharField(source='hexcolor')
    slug = serializers.SlugField(
        max_length=200,
        validators=[
            UniqueValidator(
                message='Данный tag уже существует.',
                queryset=Tag.objects.all()
            )
            ]
        )

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class IngredientShowSerializer(serializers.ModelSerializer):
    """Вывод ингредиентов по запросу."""
    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Вывод ингредиентов в рецепте"""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = IngredientInRecipe


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сохраняет количество ингредиентов в рецепте."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeShortSerializer(serializers.ModelSerializer):
    """Вывод короткого отображение рецепта."""

    class Meta:
        model = Recipe
        feilds = ('id', 'name', 'image', 'cooking_time',)


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Создаёт и редактирует рецепты."""
    ingredients = IngredientInRecipeSerializer(many=True)
    tags = TagSerializer(many=True)
    image = Base64ImageField(required=False, allow_null=True)
    author = CustomUserSerializer(read_only=True)
    cooking_time = serializers.IntegerField(
        validators=(MinValueValidator(
            1,
            message='Укажите время!',
        ),),)

    class Meta:
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time'
                  )
        model = Recipe

    def create_ingredients(self, ingredients, recipe):
        # for ingredient in ingredients:
        #     current_ingredient = Ingredient.objects.get(
        #         **ingredient)
        #     IngredientInRecipe.objects.create(
        #         achievement=current_ingredient, recipe=recipe)

        create_ingredient = [
            IngredientInRecipe(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
                )
            for ingredient in ingredients
            ]

        IngredientInRecipe.objects.bulk_create(create_ingredient)

    def create_tags(self, tags, recipe):

        for tag in tags:
            recipe.tags.add(tag)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        author = validated_data.pop('author')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_tags(tags, recipe)
        self.create_ingredients(ingredients, recipe)

        for ingredient in ingredients:
            current_ingredient = Ingredient.objects.get(
                **ingredient)
            IngredientInRecipe.objects.create(
                achievement=current_ingredient, recipe=recipe)

        return recipe

    def update(self, instance, validated_data):

        instance.tags.clear()
        IngredientInRecipe.objects.filter(recipe=instance).all().delete()
        self.create_tags(validated_data.pop('tags'), instance)
        self.create_ingredients(validated_data.pop('ingredients'), instance)
        return super().update(instance, validated_data)


class RecipeShowSerializer(serializers.ModelSerializer):
    """Вывод рецепта и списка рецептов."""
    tags = TagSerializer(many=True, read_only=True)
    author = serializers.SerializerMethodField(read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time',
                  )
        model = Recipe

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj).exists()

    def get_ingredients(self, obj):
        ingredient = IngredientInRecipe.objects.filter(recipe=obj)
        return IngredientInRecipeSerializer(ingredient, many=True).data

    def get_author(self, obj):  # подумать, как автора достать
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscriptions.objects.filter(user=request.user,
                                            author=obj).exists()


class FavoriteSerializer(serializers.ModelSerializer):
    """Добавляет рецепт в избранное."""

    class Meta:
        fields = ('user', 'recipe',)
        model = Favorite

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonimous:
            return False
        recipe = data['recipe']
        if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже в избранном!'
            )

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeShortSerializer(instance.recipe, context=context).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Добавляет рецепт в список покупок."""

    class Meta:
        fields = ('user', 'recipe',)
        model = ShoppingCart

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonimous:
            return False
        recipe = data['recipe']
        if ShoppingCart.objects.filter(user=request.user,
                                       recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже в списке покупок!'
            )

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeShortSerializer(instance.recipe, context=context).data


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Создаёт подписку."""
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )

    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        model = Subscriptions
        fields = ('user', 'author',)
        validators = (
            UniqueTogetherValidator(
                queryset=Subscriptions.objects.all(),
                message='Вы уже подписаны на этого автора!',
                fields=['user__author']
            ),
        )

    def validate(self, data):
        if self.context['request'].user != data.get('user'):
            return data
        raise serializers.ValidationError(
            'Нельзя подписаться на самого себя!'
        )

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeShortSerializer(instance.recipe, context=context).data
