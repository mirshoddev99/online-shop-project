from django.db.models import Sum, F
from product_app.models import ProductCart


def get_total_cost_in_cart(request):
    # Get the requested user
    user = request.user
    cart_products = ProductCart.objects.filter(owner__pk=user.pk)
    total_cost = cart_products.annotate(
        product_total_cost=F('quantity') * F('product__price')
    ).aggregate(total_cost=Sum('product_total_cost'))['total_cost']

    return total_cost
