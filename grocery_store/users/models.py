from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """Модель User (пользователь)"""

    username = models.CharField(
        max_length=settings.MAX_LEN_USERNAME,
        unique=True,
        verbose_name='Юзернэйм',
        validators=[RegexValidator(
            r'^[\w.@+-]+$', 'Недопустимый символ.'
        )],
    )
    first_name = models.CharField(
        max_length=settings.MAX_LEN_USERNAME,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=settings.MAX_LEN_USERNAME,
        verbose_name='Фамилия',
    )
    email = models.EmailField(
        max_length=settings.MAX_LEN_EMAIL,
        unique=True,
        verbose_name='Адрес электронной почты'
    )
    password = models.CharField(
        max_length=settings.MAX_LEN_PASSWORD,
        unique=True,
        verbose_name='Пароль',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username[:settings.SYMBOLS_QUANTITY]
