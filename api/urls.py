from django.urls import path
from api.views import SignUpAPIView, VerifyUserAPIView, GetNewVerification, UpdateUserInfoAPIView, UserLoginAPIView, \
    UserLoginRefreshAPIView, UserLogoutAPIView, ProductListAPIView, CategoryProductListAPIView, \
    SubCategoryProductListAPIView, DetailProductAPIView, WishListAPIView, CreatingWishListProductAPIView, \
    DeletingWishListProductAPIView, ProductCartListAPIView, DeleteCartProductQuantityAPIViw, DeletingCartProductView, \
    ClearProductCartAPIView

urlpatterns = [
    path('register/', SignUpAPIView.as_view()),
    path('verify-user/', VerifyUserAPIView.as_view()),
    path('new-verify/', GetNewVerification.as_view()),
    path('update-user-info/', UpdateUserInfoAPIView.as_view()),
    path('user-login/', UserLoginAPIView.as_view()),
    path('user-login-refresh/', UserLoginRefreshAPIView.as_view()),
    path('user-logout/', UserLogoutAPIView.as_view()),

    # urls of product app
    path('product-list/', ProductListAPIView.as_view()),
    path('category-product-list/<int:category_id>/', CategoryProductListAPIView.as_view()),
    path('subcategory-product-list/<int:category_id>/<int:sub_category_id>/', SubCategoryProductListAPIView.as_view()),
    path('product-detail/<int:id>/', DetailProductAPIView.as_view(), name='product_detail'),

    path('wishlist-products/', WishListAPIView.as_view()),
    path('creating-wishlist-product/<int:id>/', CreatingWishListProductAPIView.as_view()),
    path('deleting-wishlist-product/<int:id>/', DeletingWishListProductAPIView.as_view()),

    path('shoppingcart-products/', ProductCartListAPIView.as_view()),
    path('delete-product-quantity/<int:product_id>/', DeleteCartProductQuantityAPIViw.as_view()),
    path('delete-cart-product/<int:product_id>/', DeletingCartProductView.as_view()),
    path('clear-cart-products/', ClearProductCartAPIView.as_view()),

]
