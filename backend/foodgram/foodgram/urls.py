from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter

from api.views import (
    IngredientViewSet, RecipeViewSet, TagViewSet,
)
from users.views import CustomUserViewSet


router_v1 = DefaultRouter()
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router_v1.urls)),
    path('api/', include('djoser.urls')),
    re_path(r'^api/auth/', include('djoser.urls.authtoken')),
    # path('api/auth/', include('djoser.urls.jwt')),
    # path('api-token-auth/', views.obtain_auth_token),
    # path('api/v1/', include('api.urls', namespace='api')),
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
]
