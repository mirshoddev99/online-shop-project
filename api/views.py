from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render
from django.utils.datetime_safe import datetime
from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, ListCreateAPIView, CreateAPIView, DestroyAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.custom_methods import CustomPagination
from api.product_serializers import ProductSerializer, WishListSerializer, ProductCartSerializer
from api.serializers import CustomUserSerializer, SignUpSerializer, ChangeUserInfoSerializer, UserLoginSerializer, \
    UserLoginRefreshSerializeR, UserLogoutSerializer
from product_app.models import Product, WishList, ProductCart
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


# Product app view
class ProductListAPIView(ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = CustomPagination
    queryset = Product.objects.all()
    permission_classes = [permissions.AllowAny, ]


class CategoryProductListAPIView(ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = CustomPagination
    queryset = Product.objects.all()
    permission_classes = [permissions.AllowAny, ]

    def get_queryset(self):
        q = super().get_queryset().filter(category__id=self.kwargs["category_id"])
        return q


class SubCategoryProductListAPIView(ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = CustomPagination
    queryset = Product.objects.all()
    permission_classes = [permissions.AllowAny, ]

    def get_queryset(self):
        q = super().get_queryset().filter(category__id=self.kwargs["category_id"],
                                          sub_category__id=self.kwargs["sub_category_id"])
        return q


class DetailProductAPIView(APIView):
    permission_classes = [permissions.AllowAny, ]

    def get(self, request, *args, **kwargs):
        try:
            obj = Product.objects.get(id=kwargs["id"])
            serializer = ProductSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist as e:
            data = {"success": False, "error": f"{e}"}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


class WishListAPIView(ListAPIView):
    queryset = WishList.objects.all()
    pagination_class = CustomPagination
    serializer_class = WishListSerializer

    def get_queryset(self):
        q = super().get_queryset().filter(owner__id=self.request.user.id)
        return q


class CreatingWishListProductAPIView(CreateAPIView):
    queryset = WishList.objects.all()
    serializer_class = WishListSerializer

    def perform_create(self, serializer):
        if not WishList.objects.filter(product__id=self.kwargs["id"]).exists():
            product = Product.objects.get(id=self.kwargs["id"])
            serializer.is_valid(raise_exception=True)
            serializer.save(owner=self.request.user, product=product)
        else:
            raise ValidationError("Product was already added to your WishList!")


class DeletingWishListProductAPIView(DestroyAPIView):
    queryset = WishList.objects.all()
    serializer_class = WishListSerializer

    def delete(self, request, *args, **kwargs):
        try:
            obj = WishList.objects.get(product__id=kwargs["id"])
            obj.delete()
            data = {"success": True, "message": "Product has been removed from your WishList!"}
            return Response(data)
        except ObjectDoesNotExist as e:
            return Response({"error": "ObjectDoesNotExist"})


# Shopping cart
class ProductCartListAPIView(ListAPIView):
    queryset = ProductCart.objects.all()
    pagination_class = CustomPagination
    serializer_class = ProductCartSerializer

    def get_queryset(self):
        q = super().get_queryset().filter(owner__id=self.request.user.id)
        return q


# This View is used for deleting product with total quantity from the cart when the delete button is clicked on
class DeleteCartProductQuantityAPIViw(APIView):
    def delete(self, request, *args, **kwargs):
        try:
            cart_query = Q(owner__pk=request.user.pk) & Q(product__id=kwargs['product_id'])
            cart_product = get_object_or_404(ProductCart, cart_query)
            cart_product.product.quantity += cart_product.get_quantity()
            if not cart_product.product.in_active:
                cart_product.product.in_active = True
            cart_product.product.save()
            cart_product.delete()
            data = {"success": True, "message": 'Product has been removed from your cart!'}
            return Response(data, status=status.HTTP_200_OK)
        except Http404 as e:
            return Response("There is no longer this product in your shopping cart!")


# This View is used for deleting one product from the cart when the decrement button is clicked on
class DeletingCartProductView(APIView):
    def delete(self, request, **kwargs):
        try:
            cart_query = Q(owner__pk=request.user.pk) & Q(product__id=kwargs['product_id'])
            cart_product = get_object_or_404(ProductCart, cart_query)
            if cart_product.get_quantity() >= 1:
                cart_product.product.quantity += 1
                cart_product.quantity -= 1
                if not cart_product.product.in_active:
                    cart_product.product.in_active = True
                cart_product.product.save()
                cart_product.save()
                if cart_product.quantity == 0:
                    cart_product.delete()
                data = {"success": True, "message": 'Product has been removed from your cart!'}
                return Response(data, status=status.HTTP_200_OK)
        except Http404 as e:
            return Response("There is no longer this product in your shopping cart!")


class ClearProductCartAPIView(APIView):
    def delete(self, request, *args, **kwargs):
        cart_products = ProductCart.objects.all().filter(owner__pk=request.user.pk)
        if cart_products.exists():
            for p in cart_products:
                p.product.quantity += p.get_quantity()
                if not p.product.in_active:
                    p.product.in_active = True
                p.product.save()
            cart_products.delete()
            data = {"success": True, "message": "Your cart has been cleared!"}
            return Response(data)
        else:
            data = {"success": False, "message": "You have no any product to clear your Cart!"}
            return Response(data)