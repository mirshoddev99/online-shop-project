from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView, FormView, TemplateView
from django.forms import inlineformset_factory
from paypal.standard.forms import PayPalPaymentsForm
from .custom_methods import get_total_cost_in_cart
from users.models import CustomerAddress
from .forms import CreateProductForm, UpdateProductForm, ImageForm
from product_app.models import Product, Category, ProductComment, ProductImage, ProductCart, WishList, SubCategory, \
    PaymentCard


class HomeView(View):
    def get(self, request):
        all_products = Product.objects.all().filter(in_active=True)[:8]
        categories = Category.objects.all()
        contex = {"all_products": all_products, "categories": categories}
        return render(request, "product/index.html", contex)


class ProductListView(View):
    def get(self, request):
        all_products = Product.objects.all().filter(in_active=True)
        categories = Category.objects.all()

        # statement for prices
        filter_option = request.GET.get('filter')
        if filter_option == "low_to_high":
            all_products = all_products.order_by('price')  # Reassign the sorted queryset
        elif filter_option == "high_to_low":
            all_products = all_products.order_by('-price')  # Reassign the sorted queryset

        # statement for precise prices
        elif filter_option == "zero_to_fifth":
            all_products = all_products.filter(price__range=(00.00, 50.00)).order_by('price')
        elif filter_option == "fifth_to_hundred":
            all_products = all_products.filter(price__range=(50.00, 100.00)).order_by('price')
        elif filter_option == "over_hundred":
            all_products = all_products.filter(price__gte=100.00).order_by('price')

        # statement for precise tags
        elif filter_option == "Men":
            all_products = all_products.filter(category__name='Men').order_by('-created_at')
        elif filter_option == "Women":
            all_products = all_products.filter(category__name='Women').order_by('-created_at')
        elif filter_option == "Kids":
            all_products = all_products.filter(category__name='Kids').order_by('-created_at')
        elif filter_option == "Electronic":
            all_products = all_products.filter(category__name='Electronic').order_by('-created_at')

        contex = {"all_products": all_products, "categories": categories}
        return render(request, "product/product_list.html", contex)


class ProductDetailView(View):
    def get(self, request, slug):
        product = Product.objects.get(slug=slug)
        ctg_name = product.category.name
        sub_ctg_name = product.sub_category.name
        q = Q(category__name=ctg_name) & Q(sub_category__name=sub_ctg_name)
        related_products = Product.objects.all().filter(q).exclude(slug=slug)[:8]
        for img in product.images.all():
            if not img.image:
                img.delete()
        contex = {"product": product, "related_products": related_products, "ctg_name": ctg_name,
                  "sub_ctg_name": sub_ctg_name}
        return render(request, "product/product-detail.html", contex)


# Creating Product Logic
class CreateProductView(View):
    def get(self, request):
        product_form = CreateProductForm()
        image_form_set = inlineformset_factory(Product, ProductImage, form=ImageForm, extra=3)
        pr_instance = Product()
        formset = image_form_set(instance=pr_instance)
        contex = {"product_form": product_form, "formset": formset}
        return render(request, "product/new_product.html", contex)

    def post(self, request):
        product_form = CreateProductForm(request.POST)
        image_form_set = inlineformset_factory(Product, ProductImage, form=ImageForm, extra=3, can_delete=False)
        formset = image_form_set(request.POST, request.FILES)  # Instantiate the formset with the POST data and FILES

        if product_form.is_valid() and formset.is_valid():  # Check the validity of both forms
            product = product_form.save(commit=False)
            product.created_by = request.user
            product.slug = slugify(product.name)
            product.save()
            instances = formset.save(commit=False)
            for img in instances:
                img.product = product
                img.save()
            messages.success(request, "The Product has been created!")
            return redirect("products_page")

        else:
            product_form = CreateProductForm(request.POST)
            contex = {"product_form": product_form, "formset": formset}
            messages.warning(request, "Error!")
            print(formset.errors)
            print(product_form.errors)
            return render(request, "product/new_product.html", contex)


class UpdateProductView(View):
    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        update_product_form = UpdateProductForm(instance=product)
        image_form_set = inlineformset_factory(Product, ProductImage, form=ImageForm, can_delete=False, extra=0)
        formset = image_form_set(instance=product)
        contex = {"update_product_form": update_product_form, "product": product, "formset": formset}
        return render(request, "product/update_product.html", contex)

    def post(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        update_product_form = UpdateProductForm(instance=product, data=request.POST)
        image_form_set = inlineformset_factory(Product, ProductImage, form=ImageForm, can_delete=False, extra=0)
        formset = image_form_set(request.POST, request.FILES, instance=product)

        if update_product_form.is_valid() and formset.is_valid():
            product = update_product_form.save(commit=False)
            product.slug = slugify(product.name)
            product.save()
            instances = formset.save(commit=False)
            for img in instances:
                img.product = product
                img.save()
            messages.success(request, "Successfully Updated!")
            return redirect(reverse("product_detail_page", kwargs={"slug": product.slug}))
        else:
            messages.warning(request, "Error!")
            contex = {"update_product_form": update_product_form, "product": product, "formset": formset}
            return render(request, "product/update_product.html", contex)


class DeleteProductView(View):
    def get(self, request, slug):
        product = Product.objects.filter(slug=slug)
        if product.exists():
            product.delete()
            messages.warning(request, "Product has been deleted!")
            return redirect("seller_products_page")
        else:
            messages.warning(request, "There is an error occurred!")
            return redirect("home_page")


class SellerProductsListView(View):
    def get(self, request):
        query = Q(created_by__pk=request.user.pk) & Q(in_active=True)
        all_products = Product.objects.all().filter(query)
        categories = set([ctg for ctg in all_products])
        contex = {"all_products": all_products, "categories": categories}
        return render(request, "product/seller_products_list.html", contex)


class ProductCommentView(LoginRequiredMixin, View):
    def get(self, request, slug):
        product = Product.objects.get(slug=slug)
        return redirect(reverse("product_detail_page", args=product.slug))

    def post(self, request, slug):
        product = Product.objects.get(slug=slug)
        review = request.POST.get("review")
        if review:
            ProductComment.objects.create(author=request.user, product=product, body=review)
            messages.success(request, "Your review has been submitted successfully!")
        else:
            messages.warning(request, "Please fill out the form properly!")
        return redirect(reverse("product_detail_page", args=[product.slug]))


class CategoryListView(View):
    model = Product

    def get(self, request, id):
        try:
            query = Q(category__id=id) & Q(in_active=True)
            all_products = self.model.objects.all().filter(query)
            category_name = all_products[0].category
            sub_categories = all_products[0].category.subcategories.all()
            return render(request, "product/category_products.html",
                          {"all_products": all_products, "category_name": category_name,
                           "sub_categories": sub_categories})
        except IndexError:
            messages.warning(request, "All products in this category have been sold!")
            return redirect("products_page")


class SubcategoryListView(ListView):
    model = Product
    template_name = "product/subcategory_list.html"
    context_object_name = "products"

    def get_queryset(self):
        category_id = self.kwargs.get("category_id")
        subcategory_id = self.kwargs.get("subcategory_id")
        category = Category.objects.get(id=category_id)
        subcategory = SubCategory.objects.get(id=subcategory_id)
        return Product.objects.filter(category=category, sub_category=subcategory)


# ProductCart Logic
class DisplayingShoppingCart(LoginRequiredMixin, View):
    def get(self, request):
        cart_products = ProductCart.objects.all().filter(owner__pk=request.user.pk)
        if cart_products.exists():
            total_cost = ProductCart.get_final_price()
            contex = {"cart_products": cart_products, "total_cost": total_cost}
            return render(request, "product/shopping_cart.html", contex)
        else:
            messages.warning(request, "Your shopping cart is empty!")
            return redirect("products_page")


class AddingCartProductView(LoginRequiredMixin, View):
    def get(self, request, slug):
        try:
            query = Q(slug=slug) & Q(in_active=True)
            product = get_object_or_404(Product, query)
            try:
                cart_query = Q(owner__pk=request.user.pk) & Q(product__slug=slug) & Q(product__in_active=True)
                cart_product = get_object_or_404(ProductCart, cart_query)
                if cart_product.product.get_quantity() >= 1:
                    cart_product.quantity += 1
                    cart_product.product.quantity -= 1
                    cart_product.save()
                    cart_product.product.save()
                    print("Product quantity: ", cart_product.product.get_quantity())
                    if cart_product.product.get_quantity() == 0:
                        cart_product.product.in_active = False
                        print("Product has been set False")
                        cart_product.product.save()
                    messages.success(request, "Product has been added to your cart!")
                    print(f"this product is available in your cart, added one more time - ", product)
                    return redirect("shopping_cart_page")
                else:
                    messages.warning(request, "You have bought all of these products in stock!")
                    return redirect("products_page")
            except Http404:
                ProductCart.objects.create(owner=request.user, product=product)
                product.quantity -= 1
                product.save()
                print("Product quantity: ", product.get_quantity())
                if product.get_quantity() == 0:
                    product.in_active = False
                    print("Product has been set False")
                    product.save()
                messages.success(request, "Product has been added to your cart!")
                print(f"this product is not available in your cart, so added first time - ", product)
                return redirect("products_page")
        except Http404:
            messages.warning(request, "You have bought all of these products in stock!")
            return redirect("shopping_cart_page")


# This View is used for deleting one product from the cart when the decrement button is clicked on
class DeletingCartProductView(View):
    def get(self, request, slug):
        cart_query = Q(owner__pk=request.user.pk) & Q(product__slug=slug)
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
                messages.success(request, "Product has been removed from your cart!")
            return redirect("shopping_cart_page") if ProductCart.get_total_products() else redirect("products_page")


# This View is used for deleting product with total quantity from the cart when the delete button is clicked on
class DeleteProductFromCartViw(View):
    def get(self, request, slug):
        cart_query = Q(owner__pk=request.user.pk) & Q(product__slug=slug)
        cart_product = get_object_or_404(ProductCart, cart_query)
        cart_product.product.quantity += cart_product.get_quantity()
        if not cart_product.product.in_active:
            cart_product.product.in_active = True
        cart_product.product.save()
        cart_product.delete()
        messages.success(request, "Product has been removed from your cart!")
        print("Cart products", ProductCart.get_total_products())
        return redirect("shopping_cart_page") if ProductCart.get_total_products() else redirect("products_page")


class ClearingCartView(View):
    def get(self, request):
        cart_products = ProductCart.objects.all().filter(owner__pk=request.user.pk)
        for p in cart_products:
            p.product.quantity += p.get_quantity()
            if not p.product.in_active:
                p.product.in_active = True
            p.product.save()
        cart_products.delete()
        messages.success(request, "All your products hav been removed from your cart!")
        return redirect("products_page")


# WishList Logic
class WishListView(LoginRequiredMixin, ListView):
    template_name = "product/wishlist.html"
    context_object_name = "wishlist_products"
    queryset = WishList.objects.all()

    def get_queryset(self):
        q = super().get_queryset().filter(owner__pk=self.request.user.pk)
        return q


class AddingProductToWishListView(LoginRequiredMixin, View):
    def get(self, request, slug):
        wishlist_query = Q(owner__pk=request.user.pk) & Q(product__slug=slug)
        if WishList.objects.filter(wishlist_query).exists():
            messages.warning(request, "Product was already added to your WishList!")
            return redirect("displaying_wishlist_page")
        else:
            product = get_object_or_404(Product, slug=slug)
            WishList.objects.create(owner=request.user, product=product)
            messages.success(request, "Product has been added to WishList!")
            return redirect("products_page")


class DeletingProductWishListView(View):
    def get(self, request, slug):
        wishlist_query = Q(owner__pk=request.user.pk) & Q(product__slug=slug)
        product = get_object_or_404(WishList, wishlist_query)
        product.delete()
        messages.success(request, "Product has been removed from your WishList!")

        if WishList.get_total_products() >= 1:
            return redirect("displaying_wishlist_page")
        return redirect("products_page")


# Search and Filter logic
class SearchProduct(View):
    def get(self, request):
        q = request.GET.get("search_product")
        query = Q(name__icontains=q) | Q(description__icontains=q)
        products = Product.objects.all().filter(query)[:10]
        return render(request, "product/searched_products.html", {"products": products})


# Billing and Payment Logic
class CheckoutView(View):
    def get(self, request):
        if not CustomerAddress.objects.filter(customer__pk=request.user.pk).exists():
            return redirect('address_page')
        elif not PaymentCard.objects.filter(owner__pk=request.user.pk).exists():
            address = get_object_or_404(CustomerAddress, customer__pk=request.user.pk)
            cart_products = ProductCart.objects.filter(owner__pk=request.user.pk)
            total_cost = get_total_cost_in_cart(request)
            context = {'cart_products': cart_products, 'total_cost': total_cost, 'address': address}
            return render(request, "payment/checkout.html", context)
        return redirect("payment_form")

    def post(self, request):
        holder_name = request.POST.get("holder_name")
        card_number = request.POST.get("card_number")
        expire_month = request.POST.get("expire_month")
        expire_year = request.POST.get("expire_year")
        cvv = request.POST.get("cvv")
        expire_date = str(expire_month) + "/" + str(expire_year)
        PaymentCard.objects.create(owner=request.user, holder_name=holder_name, card_number=card_number,
                                   expire_date=expire_date, cvv=cvv)
        messages.success(request, "Your Payment Card was successfully created!")
        return redirect("payment_form")


class PaypalFormView(FormView):
    template_name = 'payment/paypal_form.html'
    form_class = PayPalPaymentsForm

    def get_initial(self):
        total_cost = get_total_cost_in_cart(self.request)

        return {
            'business': 'ecommercebusiness@paypal.com',
            'amount': total_cost,
            'currency_code': 'USD',
            'item_name': 'Example item',
            'invoice': 1234,
            'notify_url': self.request.build_absolute_uri(reverse('paypal-ipn')),
            'return_url': self.request.build_absolute_uri(reverse('payment_success')),
            'cancel_return': self.request.build_absolute_uri(reverse('payment_failed')),
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_cost = get_total_cost_in_cart(self.request)

        try:
            # Get the requested user
            user = self.request.user
            user_payment_card = get_object_or_404(PaymentCard, owner__pk=user.pk)
            address = get_object_or_404(CustomerAddress, customer__pk=user.pk)
            cart_products = ProductCart.objects.filter(owner__pk=user.pk)

            context['cart_products'] = cart_products
            context['total_cost'] = total_cost
            context['address'] = address
            context['user_payment_card'] = user_payment_card
            context['expire_year'] = user_payment_card.expire_date[:2]
            context['expire_month'] = user_payment_card.expire_date[3:]
            return context
        except Http404:
            messages.warning(self.request, "Error occurred!")
            return redirect("shopping_cart_page")


class PayPalSuccessView(TemplateView):
    template_name = "payment/success.html"


class PayPalFailedView(TemplateView):
    template_name = "payment/failed.html"
