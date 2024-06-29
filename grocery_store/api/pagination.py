from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    '''Кастомный пагинатор'''

    page_size = 6
