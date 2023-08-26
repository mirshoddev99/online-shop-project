from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.utils.datetime_safe import datetime
from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import CustomUserSerializer, SignUpSerializer
from users.models import CustomUser, NEW, CODE_VERIFIED


class SignUpAPIView(generics.CreateAPIView):
    serializer_class = SignUpSerializer
    permission_classes = [permissions.AllowAny, ]
    queryset = CustomUser.objects.all()


class VerifyUserAPIView(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        code = request.data.get("code")
        self.check_verify(user, code)

        data = {
            "success": True,
            "auth_status": user.auth_status,
            "access": user.token()['access'],
            "refresh": user.token()['refresh_token']
        }
        return Response(data, status=status.HTTP_200_OK)

    @staticmethod
    def check_verify(user, code):
        verifies = user.verify_codes.filter(expiration_time__gt=datetime.now(), code=code, is_confirmed=False)
        print(verifies)
        if not verifies.exists():
            raise ValidationError("Verification code has expired!")
        else:
            verifies.update(is_confirmed=True)
        if user.auth_status == NEW:
            user.auth_status = CODE_VERIFIED
            user.save()
        return True
