from django.urls import path
from api.product_views import ProductListAPIView, CategoryProductListAPIView, \
    SubCategoryProductListAPIView, DetailProductAPIView, WishListAPIView, CreatingWishListProductAPIView, \
    DeletingWishListProductAPIView, ProductCartListAPIView, DeleteCartProductQuantityAPIViw, DeletingCartProductView, \
    ClearProductCartAPIView, AddingCartProductView, ClearWishListAPIView, ProductCommentAPIView, \
    SellerProductListAPIView, CreateProductAPIView, SearchProductAPIView

urlpatterns = [
    path('product-list/', ProductListAPIView.as_view()),
    path('search-product-list/', SearchProductAPIView.as_view()),
    path('seller-products-list/', SellerProductListAPIView.as_view()),
    path('create-product/', CreateProductAPIView.as_view()),
    path('category-product-list/<int:category_id>/', CategoryProductListAPIView.as_view()),
    path('subcategory-product-list/<int:category_id>/<int:sub_category_id>/', SubCategoryProductListAPIView.as_view()),
    path('crud-product/<int:id>/', DetailProductAPIView.as_view(), name='product_detail'),
    path('product-comments/<int:product_id>/', ProductCommentAPIView.as_view()),

    path('wishlist-products/', WishListAPIView.as_view()),
    path('creating-wishlist-product/<int:id>/', CreatingWishListProductAPIView.as_view()),
    path('deleting-wishlist-product/<int:id>/', DeletingWishListProductAPIView.as_view()),
    path('clear-wishlist-product/', ClearWishListAPIView.as_view()),

    path('shoppingcart-products/', ProductCartListAPIView.as_view()),
    path('delete-product-quantity/<int:product_id>/', DeleteCartProductQuantityAPIViw.as_view()),
    path('delete-cart-product/<int:product_id>/', DeletingCartProductView.as_view()),
    path('adding-cart-product/<int:product_id>/', AddingCartProductView.as_view()),
    path('clear-cart-products/', ClearProductCartAPIView.as_view()),
]

