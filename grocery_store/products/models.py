from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Exists, OuterRef

from products.basemodels import BaseModel

User = get_user_model()


class Category(BaseModel):
    """Модель категорий"""

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name[:settings.SYMBOLS_QUANTITY]


class SubCategory(BaseModel):
    """Модель подкатегорий"""

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='category',
        verbose_name='Категория',
    )

    class Meta:
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Податегории'

    def __str__(self):
        return self.name[:settings.SYMBOLS_QUANTITY]


class ProductQuerySet(models.QuerySet):

    def add_user_annotations(self, user_id):
        return self.annotate(
            is_in_shopping_cart=Exists(
                ShoppingCart.objects.filter(
                    user_id=user_id, product__pk=OuterRef('pk')
                )
            ),
        )


class Product(models.Model):
    """Модель продуктов"""

    name = models.CharField(
        max_length=settings.MAX_LEN_NAME,
        verbose_name='Название',
    )
    slug = models.SlugField(
        max_length=settings.MAX_LEN_SLUG,
        null=True,
        verbose_name='Уникальный слаг',
        validators=[RegexValidator(
            r'^[-a-zA-Z0-9_]+$', 'Недопустимый символ.'
        )],
    )
    sub_category = models.ForeignKey(
        SubCategory,
        on_delete=models.CASCADE,
        related_name='sub_category',
        verbose_name='Подкатегория',
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена'
    )
    measurement_unit = models.CharField(
        max_length=settings.MAX_LEN_NAME,
        verbose_name='Единица измерения',
    )
    is_avaliable = models.BooleanField(
        verbose_name='В наличии',
        default=False
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return self.name[:settings.SYMBOLS_QUANTITY]


class Image(models.Model):
    """Модель изображений"""

    product = models.ForeignKey(
        Product,
        related_name='products_image',
        verbose_name='Продукт',
        on_delete=models.CASCADE
    )
    image = models.ImageField(
        upload_to='products/images/',
        null=True,
        default=None,
    )

    class Meta:
        verbose_name = 'Изображение продукта'
        verbose_name_plural = 'Изображение продуктов'

    def __str__(self):
        return self.product.name[:settings.SYMBOLS_QUANTITY]


class ShoppingCart(models.Model):
    """Модель корзины"""

    user = models.ForeignKey(
        User,
        related_name='shopping_cart',
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        related_name='product_in_shopping_cart',
        verbose_name='Продукт',
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'],
                name='unique-in-shoppingcart'
            ),
        ]

    def __str__(self):
        return (f'{self.user.username[:settings.SYMBOLS_QUANTITY]} добавил в'
                f'корзину {self.recipe.name[:settings.SYMBOLS_QUANTITY]}')
