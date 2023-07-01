from django.contrib import admin

from .models import Subscription, User


class UserAdmin(admin.ModelAdmin):
    # Перечисляем поля, которые должны отображаться в админке
    list_display = ('email', 'username',)
    # Добавляем интерфейс для поиска по тексту постов
    search_fields = ('email', 'username',)
    # Добавляем возможность фильтрации по дате
    list_filter = ('email', 'username',)


admin.site.register(Subscription)
admin.site.register(User, UserAdmin)
