from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MaxLengthValidator, RegexValidator
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from products.models import Category, Image, Product, SubCategory


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
