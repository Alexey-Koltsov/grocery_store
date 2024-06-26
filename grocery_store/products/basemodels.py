from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models


class BaseModel(models.Model):
    """Базовая модель"""

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
    image = models.ImageField(
        upload_to='products/images/',
        null=True,
        default=None,
    )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name[:settings.SYMBOLS_QUANTITY]
