from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.email import sending_code
from users.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(method_name='get_full_name')

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'full_name', 'email', 'phone', 'seller_or_customer', 'birth_date', 'avatar']

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
