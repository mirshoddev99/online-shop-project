from django.contrib import admin

from users.models import CustomUser, Contact, CustomerAddress, UserConfirmation


# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ["id", "username", "seller_or_customer", "is_active", "auth_status"]


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "email", "body"]


@admin.register(CustomerAddress)
class CustomerAddressAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'country', 'street', 'city', 'zipcode']


@admin.register(UserConfirmation)
class UserConfirmationAdmin(admin.ModelAdmin):
    list_display = ['id', 'expiration_time', 'is_confirmed', 'code', 'user']
