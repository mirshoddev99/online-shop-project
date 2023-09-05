from django.db import IntegrityError, DataError
from django.template.defaultfilters import slugify
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse

from product_app.models import Product, Category, SubCategory, WishList, ProductCart, ProductComment, ProductImage
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
        return reverse("product_detail", kwargs={"id": obj.pk}, request=request)


class ReducedProductSerializer(ProductSerializer):
    class Meta(ProductSerializer.Meta):
        fields = ['id', 'name', 'price']


class ProductCommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    product = ReducedProductSerializer(read_only=True)

    class Meta:
        model = ProductComment
        fields = ['author', 'product', 'body', 'created_at']


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    product = ReducedProductSerializer(read_only=True)

    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image']


class CreateProductSerializer(serializers.Serializer):
    created_by = serializers.CharField(read_only=True, required=False)
    category = serializers.CharField(write_only=True, required=True)
    sub_category = serializers.CharField(write_only=True, required=True)
    slug = serializers.CharField(required=False)
    name = serializers.CharField(write_only=True, required=True)
    description = serializers.CharField(write_only=True, required=True)
    price = serializers.DecimalField(max_digits=7, decimal_places=2, default=33.11)
    size = serializers.CharField(write_only=True, required=False)
    quantity = serializers.IntegerField(write_only=True, required=True)
    in_active = serializers.CharField(read_only=True, required=False)
    images = serializers.ImageField()

    @staticmethod
    def validate_category(category):
        for ctg in Category.objects.all():
            if ctg.name.lower() == category.lower():
                return ctg
        raise ValidationError("This kind of Category does not exist!")

    @staticmethod
    def validate_sub_category(sub_category):
        for sub_ctg in SubCategory.objects.all():
            if sub_ctg.name.lower() == sub_category.lower():
                return sub_ctg
        raise ValidationError("This kind of SubCategory does not exist!")

    def validate(self, data):
        slug = slugify(data.get("name"))
        if Product.objects.filter(slug=slug).exists():
            raise ValidationError({"success": False, "error": "A product with this name already exists!"})
        return data

    def create(self, validated_data):
        try:
            images = validated_data.pop('images')
            print("----Images-----\t", images)
            request = self.context.get('request')
            validated_data['slug'] = slugify(validated_data.get('name'))
            validated_data['created_by'] = request.user
            pr = Product.objects.create(**validated_data)
            ProductImageSerializer().create({"image": images, "product": pr})
            return pr
        except IntegrityError as e:
            raise IntegrityError({"error": "Some error occurred!"})

        except DataError as e:
            raise DataError({"error": "DataError occurred!"})


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
