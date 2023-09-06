from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import Http404
from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, ListCreateAPIView, CreateAPIView, DestroyAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from api.custom_methods import CustomPagination
from api.product_serializers import ProductSerializer, WishListSerializer, ProductCartSerializer, \
    ProductCommentSerializer, CreateProductSerializer
from product_app.models import Product, WishList, ProductCart, ProductComment
from users.models import CustomUser


# Product app view
class ProductListAPIView(ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = CustomPagination
    queryset = Product.objects.all()
    permission_classes = [permissions.AllowAny, ]


class CreateProductAPIView(CreateAPIView):
    serializer_class = CreateProductSerializer
    queryset = Product.objects.all()


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


class ProductCommentAPIView(ListCreateAPIView):
    queryset = ProductComment.objects.all()
    serializer_class = ProductCommentSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        query = Q(author__id=self.request.user.pk) & Q(product__id=self.kwargs['product_id'])
        return super().get_queryset().filter(query)

    def perform_create(self, serializer):
        product = Product.objects.get(id=self.kwargs["product_id"])
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user, product=product)


class SellerProductListAPIView(ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    pagination_class = CustomPagination

    def get_queryset(self):
        try:
            user = get_object_or_404(CustomUser, id=self.request.user.pk, seller_or_customer='seller')
            q = Q(created_by__pk=user.pk) & Q(in_active=True)
            return super().get_queryset().filter(q)
        except Http404:
            raise ValidationError("You are not a seller!")


# WishList
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


class ClearWishListAPIView(APIView):
    def delete(self, request, *args, **kwargs):
        wishlist_products = WishList.objects.all().filter(owner__pk=request.user.pk)
        if wishlist_products.exists():
            wishlist_products.delete()
            data = {"success": True, "message": "Your Wishlist has been cleared!"}
            return Response(data)
        else:
            data = {"success": False, "message": "Your Wishlist is empty!"}
            return Response(data)


# Shopping cart
class ProductCartListAPIView(ListAPIView):
    queryset = ProductCart.objects.all()
    pagination_class = CustomPagination
    serializer_class = ProductCartSerializer

    def get_queryset(self):
        q = super().get_queryset().filter(owner__id=self.request.user.id)
        return q


class AddingCartProductView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            query = Q(id=kwargs['product_id']) & Q(in_active=True)
            product = get_object_or_404(Product, query)
            try:
                cart_query = Q(owner__pk=request.user.pk) & Q(product__id=kwargs['product_id']) & Q(
                    product__in_active=True)
                cart_product = get_object_or_404(ProductCart, cart_query)
                if cart_product.product.get_quantity() >= 1:
                    cart_product.quantity += 1
                    cart_product.product.quantity -= 1
                    cart_product.save()
                    cart_product.product.save()
                    if cart_product.product.get_quantity() == 0:
                        cart_product.product.in_active = False
                        cart_product.product.save()
                    return Response("Product has been added to your cart!")
                else:
                    raise ValidationError("You have bought all of these products in stock!")
            except Http404:
                ProductCart.objects.create(owner=request.user, product=product)
                product.quantity -= 1
                product.save()
                if product.get_quantity() == 0:
                    product.in_active = False
                    product.save()
                return Response("Product has been added to your cart!")
        except Http404:
            raise ValidationError("This product is no active!")


# This View is used for deleting product with total quantity from the cart
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


# This View is used for deleting one product from the cart
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
            data = {"success": False, "message": "Your cart is empty!"}
            return Response(data)
