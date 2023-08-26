from product_app.models import ProductCart, WishList


def my_products(request):
    cart_products = ProductCart.objects.all().filter(owner__pk=request.user.pk)
    contex = {"cart_products": cart_products}
    return contex


def my_wishlist(request):
    counter = WishList.objects.all().filter(owner__pk=request.user.pk).count()
    contex = {"counter": counter}
    return contex
