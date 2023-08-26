import random
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.datetime_safe import datetime
from rest_framework_simplejwt.tokens import RefreshToken

USER_CHOICES = (
    ("seller", "seller"),
    ("customer", "customer"),
)

NEW, CODE_VERIFIED = ('new', 'code_verified')
EXPIRE_TIME = 3


class CustomUser(AbstractUser):
    AUTH_STATUS = (
        (NEW, NEW),
        (CODE_VERIFIED, CODE_VERIFIED),
    )
    auth_status = models.CharField(max_length=31, choices=AUTH_STATUS, default=NEW)
    seller_or_customer = models.CharField(max_length=30, choices=USER_CHOICES, blank=False, null=False,
                                          default="customer")
    avatar = models.ImageField(upload_to='images/', default='images/default.png')
    phone = models.CharField(max_length=250, default='82-10-5810-1928')
    birth_date = models.CharField(max_length=250, default='28/12/1999')

    class Meta:
        db_table = "custom_user"

    def create_verify_code(self):
        code = "".join([str(random.randint(0, 2000) % 10) for _ in range(4)])
        UserConfirmation.objects.create(code=code, user_id=self.pk)
        return code

    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            "access": str(refresh.access_token),
            "refresh_token": str(refresh)
        }

    def __str__(self):
        return self.username

    def get_status(self):
        return self.seller_or_customer

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name


class UserConfirmation(models.Model):
    code = models.CharField(max_length=4)
    user = models.ForeignKey('users.CustomUser', models.CASCADE, related_name='verify_codes')
    expiration_time = models.DateTimeField(null=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user.__str__())

    def save(self, *args, **kwargs):
        self.expiration_time = datetime.now() + timedelta(minutes=EXPIRE_TIME)
        super().save(*args, **kwargs)


class CustomerAddress(models.Model):
    customer = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="my_address")
    street = models.CharField(max_length=250, default='Pakhtakor', null=False, blank=False)
    city = models.CharField(max_length=250, default='Bukhara', null=False, blank=False)
    country = models.CharField(max_length=250, default='Uzbekistan', null=False, blank=False)
    zipcode = models.CharField(max_length=250, default='12345', null=False, blank=False)

    class Meta:
        db_table = "customer_address"


class Contact(models.Model):
    user = models.ForeignKey(CustomUser, related_name="contacts", on_delete=models.CASCADE)
    email = models.CharField(max_length=250)
    body = models.TextField()

    class Meta:
        db_table = "contact"
