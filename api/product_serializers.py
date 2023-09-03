from rest_framework import serializers
from rest_framework.reverse import reverse

from product_app.models import Product, Category, SubCategory, WishList, ProductCart
from users.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(method_name='get_full_name')

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'full_name', 'seller_or_customer']

    @staticmethod
    def get_full_name(obj):
        return obj.full_name


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['id', 'name']


class ProductSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    sub_category = SubCategorySerializer(read_only=True)
    url = serializers.SerializerMethodField(read_only=True, method_name="get_url")

    class Meta:
        model = Product
        fields = ['id', 'url', 'name',
                  'price',
                  'size',
                  'quantity',
                  'in_active',
                  'slug',
                  'category',
                  'sub_category',
                  'created_by',
                  'created_at']

    def get_url(self, obj):
        request = self.context.get('request')
        # print(self.context)
        return reverse("product_detail", kwargs={"id": obj.pk}, request=request)


class WishListSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    owner = UserSerializer(read_only=True)

    class Meta:
        model = WishList
        fields = ['id', 'owner', 'product']


class ProductCartSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    owner = UserSerializer(read_only=True)
    total_price = serializers.SerializerMethodField(method_name='get_total_price')

    class Meta:
        model = ProductCart
        fields = ['quantity', 'total_price', 'owner', 'product']

    @staticmethod
    def get_total_price(obj):
        return obj.get_total_price()

    @staticmethod
    def get_final_price(obj):
        return obj.get_final_price()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['final_total_price'] = instance.get_final_price()
        return data
