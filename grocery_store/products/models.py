from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Exists, OuterRef

from products.basemodels import BaseModel, Image

User = get_user_model()


class Category(BaseModel):
    """Модель категорий"""

    pass


class SubCategory(BaseModel):
    """Модель подкатегорий"""

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='category',
        verbose_name='Категория',
    )


class ProductQuerySet(models.QuerySet):

    def add_user_annotations(self, user_id):
        return self.annotate(
            is_in_shopping_cart=Exists(
                ShoppingCart.objects.filter(
                    user_id=user_id, product__pk=OuterRef('pk')
                )
            ),
        )


class Product(BaseModel):
    """Модель продуктов"""

    image = models.ForeignKey(
        Image,
        on_delete=models.CASCADE,
        related_name='products_image',
        verbose_name='Изображения продуктов',
    )
    sub_category = models.ForeignKey(
        SubCategory,
        on_delete=models.CASCADE,
        related_name='sub_category',
        verbose_name='Подкатегория',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user',
        verbose_name='Пользователь',
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
        related_name='product',
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
