from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password
from datetime import date
from apps.companies.models import Membership  # your Membership model



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


class ProfileSerializer(serializers.ModelSerializer):
    # avatar_url = serializers.SerializerMethodField(read_only=True)
    companies = serializers.SerializerMethodField(read_only=True)
    admin_companies = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "middle_name",
            "last_name",
            "dob",
            # "bio",
            # "avatar",
            # "avatar_url",
            "companies",
            "admin_companies",
        ]
        read_only_fields = ["id", "email", "avatar_url", "companies", "admin_companies"]


    #_____________later______________
    # def get_avatar_url(self, obj):
    #     request = self.context.get("request")
    #     if obj.avatar and hasattr(obj.avatar, "url"):
    #         return request.build_absolute_uri(obj.avatar.url) if request else obj.avatar.url
    #     return None

    def get_companies(self, obj):
        memberships = Membership.objects.filter(user=obj)
        return [{"id": m.company.id, "name": m.company.name, "role": m.role} for m in memberships]

    def get_admin_companies(self, obj):
        memberships = Membership.objects.filter(user=obj, role=Membership.Role.ADMIN)
        return [{"id": m.company.id, "name": m.company.name} for m in memberships]

    def update(self, instance, validated_data):
        """
        Allow updating only name fields, DOB, bio, and avatar
        """
        allowed_fields = ["first_name", "middle_name", "last_name", "avatar"]  # later add "dob", "bio",
        for field in allowed_fields:
            if field in validated_data:
                setattr(instance, field, validated_data[field])

        instance.save()
        return instance
