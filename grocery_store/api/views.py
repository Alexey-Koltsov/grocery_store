from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.db.models.functions import Lower
from django.http import FileResponse
from django.shortcuts import get_object_or_404, render
from djoser.serializers import SetPasswordSerializer
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAdminUser, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.serializers import (CategorySerializer, CustomUserCreateSerializer,
                             CustomUserSerializer, ProductSerializer)

from products.models import Category, Product

User = get_user_model()


def page_not_found(request, exception):
    """Страница не найдена."""
    return render(request, 'static/404.html', status=status.HTTP_404_NOT_FOUND)


class CustomUserViewSet(viewsets.ModelViewSet):
    """
    Cоздаем нового пользователя, получаем список всех пользователей,
    получаем страницу пользователя по id,
    получаем страницу текущего пользователя.
    """

    http_method_names = ('get', 'post')
    queryset = User.objects.all()
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if 'set_password' in self.request.path:
            return SetPasswordSerializer

        if 'create' in self.request.path:
            return CustomUserCreateSerializer

        return CustomUserSerializer

    @action(
        methods=['post'],
        detail=False,
        permission_classes=[AllowAny],
        url_path='create',
    )
    def create_user(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=['get'],
        serializer_class=CustomUserSerializer,
        permission_classes=[IsAuthenticated],
        detail=False,
        url_path='me',
    )
    def user_profile(self, request):
        user = self.request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['post'],
        serializer_class=SetPasswordSerializer,
        permission_classes=[IsAuthenticated],
        detail=False,
        url_path='set_password',
    )
    def change_password(self, request):
        user = self.request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    Получаем список всех продуктов, получаем продукт по id.
    """

    http_method_names = ('get')
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class ProductViewSet(viewsets.ModelViewSet):
    """
    Получаем список всех продуктов, получаем продукт по id.
    """

    http_method_names = ('get')
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Product.objects.add_user_annotations(self.request.user.pk)
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart', None
        )
        if is_in_shopping_cart is not None:
            queryset = queryset.filter(is_in_shopping_cart=is_in_shopping_cart)
        return queryset
