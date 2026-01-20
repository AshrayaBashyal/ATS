from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Company, CompanyInvite, CompanyMember

User = get_user_model()


class CompanySerializer(serializers.ModelSerializer):
    owner_email=serializers.ReadOnlyField(source="owner.email")

    class Meta:
        model = Company
        fields = ["id", "name", "description", "owner_email", "created_at", "updated_at"]


class CompanyMemberSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = CompanyMember
        fields = ["id", "user", "user_email", "role", "joined_at"]
        read_only_fields = ["joined_at"]