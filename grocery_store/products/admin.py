from django.contrib import admin

from products.models import Category, Image, Product, SubCategory


class InlineSubCategory(admin.StackedInline):
    model = SubCategory
    extra = 0


class InlineImage(admin.StackedInline):
    model = Image
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Настройка админзоны для модели категорий."""

    inlines = [InlineSubCategory]

    list_display = (
        'name',
        'image',
    )
    search_fields = ('name',)
    list_filter = ('name',)

    class Meta:
        model = Category


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    """Настройка админзоны для модели подкатегорий."""

    list_display = (
        'name',
        'category',
        'image',
    )
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Настройка админзоны для модели продуктов."""

    inlines = [InlineImage]

    list_display = (
        'name',
        'sub_category',
        'price',
        'measurement_unit',
        'pub_date',
    )
    search_fields = ('name',)
    list_filter = ('name',)


admin.site.empty_value_display = 'Не задано'
