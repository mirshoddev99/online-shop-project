from django.urls import path, include
from product_app.views import (
    HomeView, ProductListView,
    DisplayingShoppingCart, ProductDetailView,
    ProductCommentView, CreateProductView,
    SellerProductsListView, CategoryListView,
    UpdateProductView, DeleteProductView,
    AddingCartProductView, DeletingCartProductView,
    AddingProductToWishListView, WishListView,
    DeletingProductWishListView, SubcategoryListView,
    PayPalFailedView, PayPalSuccessView,
    PaypalFormView, ClearingCartView,
    SearchProduct, CheckoutView, DeleteProductFromCartViw
)


urlpatterns = [
    path('', HomeView.as_view(), name='home_page'),
    path('product-list/', ProductListView.as_view(), name='products_page'),
    path('category-product-list/<int:id>/', CategoryListView.as_view(), name='category_products_page'),
    path('category-product-list/<int:category_id>/<int:subcategory_id>', SubcategoryListView.as_view(),
         name='subcategory_products_page'),
    path('product/<slug>/', ProductDetailView.as_view(), name='product_detail_page'),

    path("create-product/", CreateProductView.as_view(), name="creating_product_page"),
    path("update-product/<slug>/", UpdateProductView.as_view(), name="updating_product_page"),
    path("delete-product/<slug>/", DeleteProductView.as_view(), name="deleting_product_page"),

    path('shopping-cart/', DisplayingShoppingCart.as_view(), name='shopping_cart_page'),
    path("adding-product-to-cart/<slug>/", AddingCartProductView.as_view(), name="adding_product_cart_page"),
    path("delete-one-cart-product/<slug>/", DeletingCartProductView.as_view(), name="delete_one_product_cart_page"),
    path("delete-cart-product/<slug>/", DeleteProductFromCartViw.as_view(), name="delete_product_cart_page"),
    path('clearing-products-cart/', ClearingCartView.as_view(), name='clearing_products_page'),

    path("wishlist-products/", WishListView.as_view(), name="displaying_wishlist_page"),
    path("adding-product-to-wishlist/<slug>/", AddingProductToWishListView.as_view(), name="wishlist_page"),
    path("delete-product-wishlist/<slug>/", DeletingProductWishListView.as_view(), name="delete_wishlist_product"),

    path('product/<slug>/comment/', ProductCommentView.as_view(), name='product_detail_comment'),
    path('seller-products-list/', SellerProductsListView.as_view(), name='seller_products_page'),

    # Search and Filter urls
    path('search-product/', SearchProduct.as_view(), name="search_product"),

    # PayPal url
    path('checkout-page/', CheckoutView.as_view(), name='checkout_page'),
    path('payment-complete/', PayPalSuccessView.as_view(), name='payment_success'),
    path('payment-failed/', PayPalFailedView.as_view(), name='payment_failed'),
    path('payment-form/', PaypalFormView.as_view(), name='payment_form'),
]

