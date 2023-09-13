from django.http import Http404
from django.utils.datetime_safe import datetime
from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from product_app.models import PaymentCard
from users_api.serializers import CustomUserSerializer, SignUpSerializer, ChangeUserInfoSerializer, UserLoginSerializer, \
    UserLoginRefreshSerializeR, UserLogoutSerializer, CustomerAddressSerializer, PaymentCardSerializer
from users.email import sending_code
from users.models import CustomUser, NEW, CODE_VERIFIED, CustomerAddress
from rest_framework import generics


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


# User Address
class CreateUserAddressAPIView(generics.CreateAPIView):
    serializer_class = CustomerAddressSerializer
    queryset = CustomerAddress.objects.all()

    def perform_create(self, serializer):
        # get requested user
        user = self.request.user
        if CustomerAddress.objects.filter(customer__id=user.id).exists():
            raise ValidationError("You have already shipping address!")
        else:
            serializer.is_valid(raise_exception=True)
            serializer.save(customer=user)


class UserAddressRetrieveDestroyUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CustomerAddressSerializer
    queryset = CustomerAddress.objects.all()
    lookup_url_kwarg = 'id'

    def get(self, request, *args, **kwargs):
        try:
            obj = get_object_or_404(CustomerAddress, customer__id=kwargs['id'])
            serializer = self.serializer_class(obj)
            return Response(serializer.data)
        except Http404:
            return Response("You have no address so you need to create your address!")

    def put(self, request, *args, **kwargs):
        try:
            obj = get_object_or_404(CustomerAddress, customer__id=kwargs['id'])
            serializer = self.serializer_class(instance=obj, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            data = {'success': True, 'message': "Your Address updated successfully!", 'data': serializer.data}
            return Response(data)
        except Http404:
            return Response("You have no address so you need to create your address!")

    def delete(self, request, *args, **kwargs):
        try:
            obj = get_object_or_404(CustomerAddress, customer__id=kwargs['id'])
            obj.delete()
            data = {'success': True, 'message': "Your Address deleted successfully!"}
            return Response(data)
        except Http404:
            return Response("You have no address so you need to create your address!")


# Payment card
class CreatePaymentCardAPIView(generics.CreateAPIView):
    serializer_class = PaymentCardSerializer
    queryset = PaymentCard.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        if not PaymentCard.objects.filter(owner__id=user.pk).exists():
            if CustomerAddress.objects.filter(customer__id=user.id).exists():
                serializer.is_valid(raise_exception=True)
                serializer.save(owner=user)
            else:
                raise ValidationError("You must add shipping address first before creating a payment card!")
        else:
            raise ValidationError("You have already payment card!")


class CRUDPaymentCardAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PaymentCardSerializer
    queryset = PaymentCard.objects.all()
    lookup_url_kwarg = 'id'

    def get(self, request, *args, **kwargs):
        try:
            obj = get_object_or_404(PaymentCard, owner__id=kwargs['id'])
            serializer = self.serializer_class(obj)
            return Response(serializer.data)
        except Http404:
            return Response(self.serializer_class.errors)

    def put(self, request, *args, **kwargs):
        try:
            obj = get_object_or_404(PaymentCard, owner__id=kwargs['id'])
            serializer = self.serializer_class(instance=obj, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            data = {'success': True, 'message': "Your Payment Card credentials updated successfully!", 'data': serializer.data}
            return Response(data)
        except Http404:
            return Response(self.serializer_class.errors)

    def delete(self, request, *args, **kwargs):
        try:
            obj = get_object_or_404(PaymentCard, owner__id=kwargs['id'])
            obj.delete()
            data = {'success': True, 'message': "Your Payment Card deleted successfully!"}
            return Response(data)
        except Http404:
            return Response(self.serializer_class.errors)
