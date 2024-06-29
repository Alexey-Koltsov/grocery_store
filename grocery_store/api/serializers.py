from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MaxLengthValidator, RegexValidator
from django.db.models import Count, F, Sum
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from products.models import Category, Image, Product, ShoppingCart, SubCategory


User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Сериализатор для создания пользователя.
    """

    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(
        required=True,
        validators=[
            MaxLengthValidator(settings.MAX_LEN_EMAIL),
        ]
    )
    username = serializers.CharField(
        required=True,
        validators=[
            UnicodeUsernameValidator,
            MaxLengthValidator(settings.MAX_LEN_USERNAME),
            RegexValidator(
                r'^[\w.@+-]+$',
                'Недопустимый символ.'
            )
        ]
    )
    first_name = serializers.CharField(
        required=True,
        validators=[
            MaxLengthValidator(settings.MAX_LEN_USERNAME),
        ]
    )
    last_name = serializers.CharField(
        required=True,
        validators=[
            MaxLengthValidator(settings.MAX_LEN_USERNAME),
        ]
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[
            MaxLengthValidator(settings.MAX_LEN_PASSWORD),
        ]
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User (пользователь).
    """

    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
        )


class SubCategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели подкатегории.
    """

    image = serializers.SerializerMethodField()

    class Meta:
        model = SubCategory
        fields = (
            'id',
            'name',
            'slug',
            'image',
        )

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели категории.
    """

    image = serializers.SerializerMethodField()
    sub_categories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            'id',
            'name',
            'slug',
            'image',
            'sub_categories',
        )

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def get_sub_categories(self, obj):
        sub_categories = SubCategorySerializer(
            SubCategory.objects.filter(category=obj),
            many=True
        ).data
        return sub_categories


class ImageSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели изображений.
    """

    class Meta:
        model = Image
        fields = (
            'id',
            'image',
        )


class ProductSerializer(serializers.ModelSerializer):
    """
    Получение списка рецептов и рецепта по id.
    """

    id = serializers.IntegerField(read_only=True)
    images = serializers.SerializerMethodField()
    sub_category = SubCategorySerializer(
        read_only=True,
    )
    category = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.BooleanField()

    def get_images(self, obj):
        images = ImageSerializer(
            Image.objects.filter(product=obj),
            many=True
        ).data
        return images

    def get_category(self, obj):
        sub_category = get_object_or_404(SubCategory, name=obj.sub_category)
        category = CategorySerializer(
            get_object_or_404(Category, name=sub_category.category),
        ).data
        category.pop('sub_categories')
        return category

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'slug',
            'images',
            'sub_category',
            'category',
            'price',
            'measurement_unit',
            'is_in_shopping_cart',
        )


class ProductMinifieldSerializer(serializers.ModelSerializer):
    """
    Получение списка рецептов и рецепта по id.
    """

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'slug',
            'price',
            'measurement_unit',
        )


class ProductInShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для добавленеия продукта в корзину,
    изменения его количества в корзине и
    для удаления из корзины.
    """

    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )
    product = ProductMinifieldSerializer(
        read_only=True,
    )
    summ = serializers.SerializerMethodField()

    def get_queryset(self):
        return self.context['request'].user.shopping_cart.all().annotate(
            total_summ=Sum("product__price" * "amount")
        )

    def validate_product(self, value):
        if self.context['request'].method == 'POST':
            if self.get_queryset().filter(user=self.context['request'].user,
                                          product=value).exists():
                raise serializers.ValidationError(
                    'Продукт уже добавлен в корзину!'
                )
        return value

    def get_summ(self, obj):
        summ = obj.amount * obj.product.price
        return summ

    class Meta:
        model = ShoppingCart
        fields = ('user', 'product', 'amount', 'summ')


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для получения всех товаров корзины."""

    list_of_products = serializers.SerializerMethodField()
    total_summ = serializers.SerializerMethodField()
    products_count = serializers.SerializerMethodField()

    def get_queryset(self):
        return User.objects.filter(username=self.context['request'].user)

    def get_total_summ(self, obj):
        return obj.shopping_cart.all().annotate(
            summ=F('product__price') * F('amount')
        ).aggregate(total_summ=Sum('summ'))['total_summ']

    def get_products_count(self, obj):
        return obj.shopping_cart.count()

    def get_list_of_products(self, obj):
        return ProductInShoppingCartSerializer(
            ShoppingCart.objects.filter(user=obj),
            many=True
        ).data

    class Meta:
        model = User
        fields = ('list_of_products', 'total_summ', 'products_count')
