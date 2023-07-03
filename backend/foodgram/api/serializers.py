from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from recipes.models import (
    Favorite, Ingredient, IngredientInRecipe,
    Recipe, ShoppingCart, Tag
)
from users.serializers import CustomUserSerializer

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тег."""
    color = serializers.CharField(source='hexcolor')
    slug = serializers.SlugField(
        max_length=200,
        validators=[
            UniqueValidator(
                message='Данный tag уже существует.',
                queryset=Tag.objects.all()
            )])

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class IngredientShowSerializer(serializers.ModelSerializer):
    """Вывод ингредиентов по GET-запросу."""
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


class IngredientAddToRecipeSerializer(serializers.Serializer):
    """Сохраняет количество ингредиентов в рецепте."""
    amount = serializers.IntegerField(
        validators=(MinValueValidator(
            1,
            message='Укажите количество!',
        ),),)
    id = serializers.IntegerField()


class RecipeShortSerializer(serializers.ModelSerializer):
    """Вывод короткого отображение рецепта."""
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Создаёт и редактирует рецепты."""
    ingredients = IngredientAddToRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(required=False, allow_null=True)
    author = CustomUserSerializer(read_only=True)
    cooking_time = serializers.IntegerField(
        validators=(MinValueValidator(
            1,
            message='Укажите время!',
        ),),)

    class Meta:
        fields = ('author', 'ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time'
                  )
        read_only_fields = ('author',)
        model = Recipe

    def create_ingredients(self, ingredients, recipe):
        create_ingredient = [
            IngredientInRecipe(
                recipe=recipe,
                amount=ingredient.get("amount"),
                ingredient_id=ingredient.get('id'),
            )
            for ingredient in ingredients
        ]
        IngredientInRecipe.objects.bulk_create(create_ingredient)

    def create_tags(self, tags, recipe):

        recipe.tags.set(tags)

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        author = validated_data.pop('author')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_tags(tags, recipe)
        self.create_ingredients(ingredients, recipe)

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.tags.clear()
        IngredientInRecipe.objects.filter(recipe=instance).all().delete()
        self.create_tags(validated_data.pop('tags'), instance)
        self.create_ingredients(validated_data.pop('ingredients'), instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeShowSerializer(
            instance, context={'request': self.context.get('request')}
        ).data


class RecipeShowSerializer(serializers.ModelSerializer):
    """Вывод рецепта и списка рецептов."""
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
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
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj).exists()

    def get_ingredients(self, obj):
        ingredient = IngredientInRecipe.objects.filter(recipe=obj)
        return IngredientInRecipeSerializer(ingredient, many=True).data
