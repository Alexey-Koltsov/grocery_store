from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from products.models import Product

User = get_user_model()


class CustomCreateUpdateDestroyMixin(generics.CreateAPIView,
                                     generics.UpdateAPIView,
                                     generics.DestroyAPIView):
    """
    Миксин для создания, изменения и удаления объектов избранного и корзины.
    """

    permission_classes = (IsAuthenticated,)
    lookup_field = 'product__id'
    lookup_url_kwarg = 'id'

    def check_product_exist(self):
        if not Product.objects.filter(
            id=self.kwargs['id']
        ).exists():
            return Response(
                'Такого объекта не существует!',
                status=status.HTTP_400_BAD_REQUEST
            )

    def create(self, request, *args, **kwargs):
        self.check_product_exist()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        product = get_object_or_404(Product, id=self.kwargs['id'])
        serializer.save(
            user=self.request.user,
            product=product
        )

    def check_product_in_shopping_cart_exist(self):
        if not self.get_queryset().exists():
            return Response(
                'Такого объекта не существует!',
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        if not self.get_queryset().exists():
            return Response(
                'Такого объекта не существует!',
                status=status.HTTP_400_BAD_REQUEST
            )
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        if not self.get_queryset().exists():
            return Response(
                'Такого объекта не существует!',
                status=status.HTTP_400_BAD_REQUEST
            )
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            'Объект удален!',
            status=status.HTTP_204_NO_CONTENT
        )
