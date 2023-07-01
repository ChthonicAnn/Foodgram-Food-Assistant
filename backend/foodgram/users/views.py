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
from rest_framework.permissions import IsAuthenticated  # AllowAny
from rest_framework.response import Response

from api.paginators import CustomPagination
# from api.permissions import (
#     IsAdminOrAuthorOrReadOnly,  # IsAdmin, IsAdminOrReadOnly,
# )
from .models import Subscription

from .serializers import CustomUserSerializer
from .serializers import SubscriptionShowSerializer

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Вьюсет для юзера."""
    queryset = User.objects.all()
    # lookup_field = 'username'
    serializer_class = CustomUserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    # permission_classes = (IsAdminOrAuthorOrReadOnly,)
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
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)

        if self.request.method == 'POST':
            if not Subscription.objects.filter(user=user,
                                               author=author).exists():
                if user != author:
                    Subscription.objects.create(
                        user=request.user,
                        author=author
                    )
                    serializer = CustomUserSerializer(instance=author)
                    return Response(serializer.data,
                                    status=status.HTTP_201_CREATED,
                                    )
                return Response({'errors': 'Вы не можете подписаться на себя'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({'errors': 'Вы уже подписаны на этого автора'},
                            status=status.HTTP_400_BAD_REQUEST
                            )

        if self.request.method == 'DELETE':
            if Subscription.objects.filter(user=user, author=author).exists():
                Subscription.objects.filter(user=user, author=author).delete()
                return Response(
                    {'errors': 'Вы больше не подписаны на этого автора'},
                    status=status.HTTP_201_CREATED,
                )
            return Response({'errors': 'Вы не следите за этим автором'},
                            status=status.HTTP_400_BAD_REQUEST
                            )

    @action(detail=False, methods=('get',),
            permission_classes=[IsAuthenticated],)
    def subscriptions(self, request):
        queryset = Subscription.objects.filter(user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionShowSerializer(
            pages,
            many=True,
            context={'request': request},
        )
        return self.get_paginated_response(serializer.data)
