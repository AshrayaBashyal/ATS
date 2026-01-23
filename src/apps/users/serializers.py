from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password
from datetime import date


class UserSerializer(serializers.ModelSerializer):
    """Read-only serializer for user info"""

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "middle_name",
            "last_name",
            "dob",
            "is_verified",
            "is_active",
            "is_staff",
            "date_joined",
        ]
        read_only_fields = fields  # Everything is read-only for safety


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for registering new users"""
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["email", "password", "first_name", "middle_name", "last_name", "dob"]

    def validate_dob(self, value):
        today = date.today()
        if value >= today:
            raise serializers.ValidationError("Date of birth must be in the past.")
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 13:
            raise serializers.ValidationError("You must be at least 13 years old.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(trim_whitespace=True)
    password = serializers.CharField(write_only=True)


class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField(trim_whitespace=True)
    otp = serializers.CharField(max_length=6)


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(trim_whitespace=True)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(trim_whitespace=True)
    otp = serializers.CharField(max_length=6)
    password = serializers.CharField(write_only=True, validators=[validate_password])


class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
