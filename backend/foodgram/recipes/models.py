from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        unique=True,
        max_length=50,
    )
    slug = models.SlugField(
        verbose_name='Ссылка',
        unique=True,
        max_length=50
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


class Ingredients(models.Model):
    name = models.CharField(
        verbose_name='Название',
    )
    measure = models.CharField(
        verbose_name='Единицы измерения',
    )

    class Meta:
        verbose_name = 'Ингридиент',
        verbose_name_plural = 'Ингридиенты'
        ordering = ('id',)

    def __str__(self):
        return self.name


class Recipes(models.Model):
    author = models.ForeignKey(
        User,
        related_name='recepes',
        verbose_name='Автор публикации',
        on_delete=models.CASCADE
    )
    name = models.CharField(
        verbose_name='Название', max_length=200
    )
    image = models.ImageField(
        verbose_name='Картинка', upload_to='photo_recipes/', null=True
    )
    description = models.TextField(verbose_name='Текстовое описание')
    tag = models.ManyToManyField(
        Tag,
        related_name='tag',
        verbose_name='Тэг',
    )
    time = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(
            1,
            message='Укажите время!',
        ),),
        verbose_name='Время приготовления',
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        related_name='ingredients',
        verbose_name='Ингридиенты',
    )

    class Meta:
        verbose_name = 'Рецепт',
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class Favorites(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='in_favorite',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Избранный рецепт',
    )

    def __str__(self):
        return f'Рецепт {self.recipe} у вас в избранном'


class IngredientsInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='recipe_with',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='in_recipe',
        verbose_name='Ингридиент',
    )
    quantity = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(
            1,
            message='Укажите количество!',
        ),),
        verbose_name=('Количество'),
    )

    def __str__(self):
        return f'Рецепт {self.recipe} у вас в избранном'
