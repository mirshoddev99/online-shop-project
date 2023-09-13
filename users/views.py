from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordResetView
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View

from .forms import RegistrationForm, CustomPasswordResetForm
from .models import Contact, CustomUser, CustomerAddress
from .email import sending_email


class RegisterView(View):
    def get(self, request):
        return render(request, "users/register.html")

    def post(self, request):
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("confirm_password")
        seller_or_customer = request.POST.get("seller_or_customer").lower()
        if password == password2:
            # sending an email
            sending_email(email, username)
            hashed_password = make_password(password)  # Hash the password
            CustomUser.objects.create(username=username, first_name=first_name, last_name=last_name, email=email,
                                      password=hashed_password,
                                      seller_or_customer=seller_or_customer)
            messages.success(request, "You have successfully registered!")
            return redirect("login_page")
        else:
            messages.warning(request, "Passwords mismatch!")
            return render(request, "users/register.html")


class TestRegisterView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, "users/register2.html", {"form": form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            messages.success(request, "Registration was successful!")
            return redirect("login_page")
        else:
            form = RegistrationForm(request.POST)
            messages.success(request, "Something went wrong!")
            print(form.errors)
            return render(request, "users/register2.html", {"form": form})


class CustomLoginView(View):
    def get(self, request):
        return render(request, "users/login.html")

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, "You Have Successfully Logged in!")
            return redirect('home_page')
        messages.warning(request, "username or password mismatch!")
        return render(request, "users/login.html")


class CustomLogOutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.success(request, "You Have Successfully Logged Out!")
        return redirect('login_page')


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm


class ProfileView(LoginRequiredMixin, View):
    def get(self, request, username):
        try:
            profile = get_object_or_404(CustomUser, username=username)
            return render(request, "users/profile.html", {"profile": profile})
        except Http404:
            return HttpResponse(content={"success": False, "error": "profile not found"})


class EditProfileView(LoginRequiredMixin, View):
    def get(self, request):
        try:
            user = get_object_or_404(CustomUser, pk=request.user.pk)
            return render(request, "users/edit_profile.html", {"user": user})
        except Http404:
            return HttpResponse(content={"success": False, "error": "profile not found"})

    def post(self, request):
        user = get_object_or_404(CustomUser, pk=request.user.pk)
        # print(request.POST)
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        birth_date = request.POST.get("birthday")
        image = request.FILES.get("image")
        print("Image is ", image)

        # updating user attributes
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.phone = phone
        user.birth_date = birth_date
        if image:
            user.avatar = image
        user.save()
        messages.success(request, "Your Profile has been updated successfully!")
        return redirect(reverse("profile_page", kwargs={"username": user.username}))


class CustomerAddressView(LoginRequiredMixin, View):
    def get(self, request):
        if not CustomerAddress.objects.filter(customer__pk=request.user.pk).exists():
            return render(request, "users/address.html")
        return redirect('edit_address_page')

    def post(self, request):
        street = request.POST.get("street")
        country = request.POST.get("country")
        city = request.POST.get("city")
        zipcode = request.POST.get("zipcode")
        CustomerAddress.objects.create(
            customer=request.user,
            street=street,
            city=city,
            country=country,
            zipcode=zipcode)
        messages.success(request, "Your address has been completed successfully!")
        return redirect(reverse("profile_page", kwargs={"username": request.user.username}))


class CustomerAddressEditView(LoginRequiredMixin, View):
    def get(self, request):
        try:
            address = get_object_or_404(CustomerAddress, customer__pk=request.user.pk)
            return render(request, "users/edit_address.html", {"address": address})
        except Http404:
            return HttpResponse(content={"success": False, "error": "CustomerAddress not found"})

    def post(self, request):
        address = get_object_or_404(CustomerAddress, customer__pk=request.user.pk)
        street = request.POST.get("street")
        country = request.POST.get("country")
        city = request.POST.get("city")
        zipcode = request.POST.get("zipcode")

        address.customer = get_object_or_404(CustomUser, pk=request.user.pk)
        address.street = street
        address.country = country
        address.city = city
        address.zipcode = zipcode
        address.save()
        messages.success(request, "Your address has been updated successfully!")
        return redirect(reverse("profile_page", kwargs={"username": request.user.username}))


class ContactView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "users/contact.html")

    def post(self, request):
        email = request.POST.get("email")
        msg = request.POST.get("msg")

        if email and msg:
            Contact.objects.create(user=request.user, email=email, body=msg)
            messages.success(request, "your message has been successfully submitted!")
            return redirect("home_page")
        messages.warning(request, "Fill out the both fields!")
        return render(request, "users/contact.html")
