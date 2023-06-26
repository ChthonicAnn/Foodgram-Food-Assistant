from django.contrib.auth import get_user_model
# from django.contrib.auth.tokens import default_token_generator
# from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import filters
# from rest_framework import mixins
# from rest_framework import permissions
from rest_framework import response
from rest_framework import status
# from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.paginators import CustomPagination
# from api.permissions import (
#     IsAdmin, IsAdminOrReadOnly, IsAdminOrAuthorOrReadOnly
# )
from .models import Subscriptions

from .serializers import SubscriptionsSerializer, CustomUserSerializer

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    lookup_field = 'username'
    serializer_class = CustomUserSerializer
    filter_backends = (filters.SearchFilter, )
    search_fields = ('username',)
    permission_classes = ([AllowAny],)
    pagination_class = CustomPagination

    @action(methods=['patch', 'get'], detail=False, url_path='me',
            permission_classes=[IsAuthenticated],)
    def me(self, request):
        instance = self.request.user
        serializer = self.get_serializer(instance)
        if self.request.method == 'PATCH':
            serializer = self.get_serializer(
                instance, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return response.Response(serializer.data)

    @action(detail=True, methods=('post', 'delete'),
            permission_classes=[IsAuthenticated],)
    def subscribe(self, request, pk=None):
        user = request.user
        author = get_object_or_404(User, pk=pk)

        if self.request.method == 'POST':
            if not Subscriptions.objects.filter(user=user,
                                                author=author).exists():
                if request.user != author:
                    Subscriptions.objects.create(
                        user=request.user,
                        author=author
                    )
                    serializer = SubscriptionsSerializer()
                    return Response(serializer.data)
            raise Response(status=status.HTTP_204_NO_CONTENT)

        if self.request.method == 'DELETE':
            if Subscriptions.objects.filter(user=user, author=author).exists():
                Subscriptions.objects.filter(user=user, author=author).delete()
            raise Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=('get',),
            permission_classes=[IsAuthenticated],)
    def subscription(self, request):
        queryset = Subscriptions.objects.filter(user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
