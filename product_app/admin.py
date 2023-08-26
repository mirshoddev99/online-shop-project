from django.contrib import admin
from product_app.models import Product, Category, ProductCart, ProductComment, ProductImage, WishList, SubCategory


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'quantity', 'in_active', 'created_at']
    list_filter = ["id", 'name', 'created_at', 'size']
    search_fields = ['name', 'id', 'created_at']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ["id", 'product', "image"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", 'name']
    list_filter = ["id", 'name']
    search_fields = ['name', 'id']


@admin.register(ProductCart)
class ProductCartAdmin(admin.ModelAdmin):
    list_display = ["owner", 'product', 'quantity']


@admin.register(WishList)
class WishListAdmin(admin.ModelAdmin):
    list_display = ["owner", 'product']


@admin.register(ProductComment)
class ProductCommentAdmin(admin.ModelAdmin):
    list_display = ["author", 'product', "body"]


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['category', 'name']

