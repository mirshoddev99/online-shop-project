from django.db import models
from users.models import CustomUser


class Category(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, related_name="subcategories", on_delete=models.CASCADE)
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=950)
    description = models.CharField(max_length=250)
    price = models.DecimalField(decimal_places=2, max_digits=7)
    size = models.CharField(max_length=4, blank=True, null=True)
    quantity = models.IntegerField(default=1)
    in_active = models.BooleanField(default=True)
    slug = models.SlugField(max_length=250)
    category = models.ForeignKey(Category, related_name="product", on_delete=models.CASCADE)
    sub_category = models.ForeignKey(SubCategory, related_name="product", on_delete=models.CASCADE)
    created_by = models.ForeignKey(CustomUser, related_name="product", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def get_quantity(self):
        return self.quantity

    def get_slug(self):
        return self.slug

    def get_price(self):
        return self.price


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="images/", blank=True, null=True)

    def __str__(self):
        return f"created by {self.product.name}"


class ProductComment(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="comments", on_delete=models.CASCADE)
    body = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Left comment by {self.author.username}"


class ProductCart(models.Model):
    owner = models.ForeignKey(CustomUser, related_name="my_cart", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="product_cart", on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"created by {self.owner.username}"

    def get_quantity(self):
        return self.quantity

    @staticmethod
    def get_total_products():
        return ProductCart.objects.count()

    def get_total_price(self):
        return self.quantity * self.product.get_price()

    @staticmethod
    def get_final_price():
        final_price = 0
        for pr in ProductCart.objects.all():
            final_price += pr.get_total_price()
        return final_price


class WishList(models.Model):
    owner = models.ForeignKey(CustomUser, related_name="my_wishlist", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"created by {self.owner.username}"

    @staticmethod
    def get_total_products():
        return WishList.objects.count()


class PaymentCard(models.Model):
    holder_name = models.CharField(max_length=250, blank=False, null=True)
    card_number = models.CharField(max_length=250, blank=False, null=True)
    expire_month = models.CharField(max_length=250, blank=False, null=True)
    cvv = models.CharField(max_length=250, blank=False, null=True)
    expire_date = models.CharField(max_length=250, blank=False, null=True)
    owner = models.ForeignKey(CustomUser, related_name="my_card", on_delete=models.CASCADE)

    def __str__(self):
        return self.holder_name
