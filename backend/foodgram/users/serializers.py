from django.contrib.auth import get_user_model
# from django.contrib.auth.tokens import default_token_generator
# from django.contrib.auth.models import User
# from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from api.serializers import RecipeShortSerializer
from users.models import Subscriptions

User = get_user_model()


class CustomUserCreateSerializer(UserSerializer):
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                message='Аккаунт с этим адресом уже существует',
                queryset=User.objects.all()
                )
            ]
        )
    username = serializers.CharField(
        validators=[
            UniqueValidator(
                message='Пользователь с таким именем уже существует',
                queryset=User.objects.all()
            ),
        ]
    )

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed',
        )


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed',
        )

    def validate_role(self, value):
        user = self.context.get('request').user
        if not user.is_admin:
            return 'user'
        return value

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscriptions.objects.filter(
            user=request.user, author=obj).exists()


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')

    @staticmethod
    def validate_username(username):
        error_names = ('me',)
        if username in error_names:
            raise serializers.ValidationError(
                f"Нельзя использовать имя '{username}'!"
            )
        return username


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Создаём подписку."""
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
