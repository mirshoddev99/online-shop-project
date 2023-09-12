from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken

from users.email import sending_code
from users.models import CustomUser, CODE_VERIFIED, CustomerAddress


class CustomUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(method_name='get_full_name')

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'full_name', 'email', 'phone', 'seller_or_customer']

    @staticmethod
    def get_full_name(obj):
        return obj.full_name


class SignUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    full_name = serializers.SerializerMethodField(method_name="get_full_name")

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'confirm_password', "username", 'full_name']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('confirm_password')
        user = super().create(validated_data)
        user.set_password(password)
        code = user.create_verify_code()
        sending_code(user.email, code)
        user.save()
        return user

    @staticmethod
    def get_full_name(obj):
        return obj.full_name

    @staticmethod
    def validate_username(username):
        if len(username) < 5 or len(username) > 30:
            raise ValidationError("Username must be between 5 and 30 characters")
        if username.isdigit():
            raise ValidationError("This username is entirely numeric")
        return username

    @staticmethod
    def validate_email(email):
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("This email already in use! ")
        return email

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['username'] = instance.username
        data['success'] = True
        data['message'] = 'You have successfully signed up!'
        data.update(instance.token())
        return data


class ChangeUserInfoSerializer(serializers.Serializer):
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    email = serializers.CharField(write_only=True, required=False)
    phone = serializers.CharField(write_only=True, required=False)
    birth_date = serializers.CharField(write_only=True, required=False)

    @staticmethod
    def validate_email(email):
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("This email already in use! ")
        return email

    @staticmethod
    def validate_birth_date(birth_date):
        if len(birth_date) < 10 or len(birth_date) > 10:
            raise ValidationError("The birth date length should be 10 characters!")
        return birth_date

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.email = validated_data.get("email", instance.email)
        instance.phone = validated_data.get("phone", instance.phone)
        instance.birth_date = validated_data.get("birth_date", instance.birth_date)
        instance.save()
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['success'] = True
        data['auth_status'] = instance.auth_status
        data['message'] = 'Successfully updated!'
        if instance.full_name != "":
            data["full_name"] = instance.full_name
        return data


class UserLoginSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.fields['username'] = serializers.CharField(write_only=True, required=True)
        self.fields['password'] = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        self.auth_validate(data)
        print(data)
        if self.user.auth_status != CODE_VERIFIED:
            raise PermissionDenied("You can not log in because of you have no permission!")
        data = self.user.token()
        data["auth_status"] = self.user.auth_status
        data["success"] = True
        data["message"] = "You have successfully logged in!"
        if self.user.full_name != "":
            data["full_name"] = self.user.full_name
        return data

    def auth_validate(self, data):
        authentication_kwargs = {
            self.username_field: data['username'],
            "password": data["password"]
        }
        user = authenticate(**authentication_kwargs)
        print("User - ", user)
        print(data)
        if user is not None:
            self.user = user
        else:
            raise ValidationError({
                "success": False,
                "message": "Sorry, password or username you entered is incorrect. Please check it out and try again!"
            })


class UserLoginRefreshSerializeR(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        access_token_instance = AccessToken(data['access'])
        user_id = access_token_instance['user_id']
        user = get_object_or_404(CustomUser, id=user_id)
        update_last_login(None, user)
        data['success'] = True
        data['message'] = "Your access token has been updated!"
        return data


class UserLogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class CustomerAddressSerializer(serializers.ModelSerializer):
    customer = CustomUserSerializer(required=False)
    street = serializers.CharField(required=True)
    city = serializers.CharField(required=True)
    country = serializers.CharField(required=True)
    zipcode = serializers.CharField(max_length=5)

    class Meta:
        model = CustomerAddress
        fields = ["customer", 'street', 'city', 'country', 'zipcode']

    @staticmethod
    def validate_zipcode(zipcode):
        if not zipcode.isdigit():
            raise ValidationError("You must enter only digits!")
        return zipcode
