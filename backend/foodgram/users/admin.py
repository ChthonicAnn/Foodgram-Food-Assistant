from django.contrib import admin

from .models import Subscription, User


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username',)
    search_fields = ('email', 'username',)
    list_filter = ('email', 'username',)


admin.site.register(Subscription)
admin.site.register(User, UserAdmin)
