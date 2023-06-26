from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        unique=True,
        max_length=200,
    )
    slug = models.SlugField(
        verbose_name='Ссылка',
        unique=True,
        max_length=200
    )
    hexcolor = models.CharField(
        verbose_name='Цветовой HEX-код',
        default="#ffffff",
        unique=True,
        max_length=7,
        validators=[
            RegexValidator(
                regex=r'#([a-fA-F0-9]{6})',
                message='Введите корректное значение HEX кода цвета',
            )
        ],
    )

    class Meta:
        verbose_name = 'Тэг',
        verbose_name_plural = 'Тэги'
        ordering = ('id',)

    def __str__(self):
        return self.id


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единицы измерения',
    )

    class Meta:
        verbose_name = 'Ингридиент',
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор публикации',
        related_name='recipes',
        on_delete=models.CASCADE
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=200
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='photo/recipes/',
        null=True,
        default=None,
    )
    description = models.TextField(
        verbose_name='Текстовое описание',
    )
    tag = models.ManyToManyField(
        Tag,
        verbose_name='Тэг',
        related_name='tag',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(
            1,
            message='Укажите время!',
        ),),
        verbose_name='Время приготовления',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='ingredients',
        verbose_name='Ингридиенты',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        verbose_name = 'Рецепт',
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='in_favorite',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Избранный рецепт',
    )

    def __str__(self):
        return f'Рецепт {self.recipe} в избранном у {self.user}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_list',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'список покупок'

    def __str__(self):
        return f'Рецепт {self.recipe} в списке покупок у {self.user}'


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_with',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='in_recipe',
        verbose_name='Ингридиент',
    )
    amount = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(
            1,
            message='Укажите количество!',
        ),),
        verbose_name=('Количество'),
    )

    def __str__(self):
        return f'Рецепт {self.recipe} у вас в избранном'
