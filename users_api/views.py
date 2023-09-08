
from django.utils.datetime_safe import datetime
from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from users_api.serializers import CustomUserSerializer, SignUpSerializer, ChangeUserInfoSerializer, UserLoginSerializer, \
    UserLoginRefreshSerializeR, UserLogoutSerializer
from users.email import sending_code
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


class GetNewVerification(APIView):
    permission_classes = [permissions.AllowAny, ]

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.verify_codes.filter(expiration_time__gt=datetime.now(), is_confirmed=False).exists():
            raise ValidationError("Your verification code is still valid to user!")
        else:
            code = user.create_verify_code()
            sending_code(user.email, code)
            data = {
                "success": True, "message": "New verification code has been sent",
                "access": user.token()['access'],
                "refresh": user.token()['refresh_token']
            }
            return Response(data)


class UpdateUserInfoAPIView(APIView):
    def put(self, request, *args, **kwargs):
        instance = CustomUser.objects.get(id=request.user.pk)
        serializer = ChangeUserInfoSerializer(instance=instance, partial=True, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginAPIView(TokenObtainPairView):
    serializer_class = UserLoginSerializer


class UserLoginRefreshAPIView(TokenRefreshView):
    serializer_class = UserLoginRefreshSerializeR


class UserLogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = UserLogoutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            msg = {"success": True, "message": "You have successfully logged out!"}
            return Response(data=msg)

        except TokenError as e:
            raise TokenError(e)