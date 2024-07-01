from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (CategoryViewSet, CustomUserViewSet,
                       ProductViewSet, APIShoppingCartCreateUpdateDestroy)

app_name = 'api'

router_api_01 = DefaultRouter()

router_api_01.register('users', CustomUserViewSet, basename='users')
router_api_01.register('categories', CategoryViewSet, basename='categories')
router_api_01.register('products', ProductViewSet, basename='products')

shopping_cart_urlpatterns = [
    path('products/<int:id>/shopping_cart/',
         APIShoppingCartCreateUpdateDestroy.as_view(), name='shopping_cart'),
    ]

urlpatterns = [
    path('', include(router_api_01.urls)),
    path('', include(shopping_cart_urlpatterns)),
    path('auth/', include('djoser.urls.authtoken')),
]
