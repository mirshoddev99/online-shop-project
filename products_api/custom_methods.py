from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from users.models import CustomUser


def get_user(username, password):
    global user
    try:
        user = CustomUser.objects.filter(username=username, password=password).first()
    except ObjectDoesNotExist:
        raise ValidationError("User not found or invalid credentials!")
    return user


class CustomPagination(PageNumberPagination):
    page_size = 5
    max_page_size = 100
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            "previous": self.get_previous_link(),
            "next": self.get_next_link(),
            "count": self.page.paginator.count,
            "results": data
        })
