from rest_framework import serializers
from apps.companies.models import Company, Membership, Invite


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "name", "description", "created_at"]


class MembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Membership
        fields = ["id", "user_email", "role", "joined_at"]


class InviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invite
        fields = ["id", "email", "role", "status", "created_at"]


class CompanyCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_blank=True)


class SendInviteSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=Membership.Role.choices)


class ChangeRoleSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=Membership.Role.choices)


class MyInviteSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True)
    invited_by = serializers.SerializerMethodField()
    recipient = serializers.SerializerMethodField()

    class Meta:
        model = Invite
        fields = [
            "id",
            "company_name",
            "role",
            "status",
            "created_at",
            "invited_by",
            "recipient",
        ]

    def get_invited_by(self, obj):
        user = obj.invited_by
        if not user:
            return None
        full_name = " ".join(
            filter(None, [user.first_name, getattr(user, "middle_name", ""), user.last_name])
        )
        return {
            "id": user.id,
            "email": user.email,
            "full_name": full_name or None,
        }

    def get_recipient(self, obj):
        company = obj.company
        if not company:
            return None
        return {
            "id": company.id,
            "name": company.name,
            "description": company.description,
        }
















# from rest_framework import serializers
# from django.contrib.auth import get_user_model
# from ..models import Company, CompanyInvite, CompanyMember

# User = get_user_model()


# class CompanySerializer(serializers.ModelSerializer):
#     owner_email=serializers.ReadOnlyField(source="owner.email")

#     class Meta:
#         model = Company
#         fields = ["id", "name", "description", "owner_email", "created_at", "updated_at"]


# class CompanyMemberSerializer(serializers.ModelSerializer):
#     user_email = serializers.EmailField(source="user.email", read_only=True)

#     class Meta:
#         model = CompanyMember
#         fields = ["id", "user", "user_email", "role", "joined_at"]
#         read_only_fields = ["joined_at"]


# class CompanyInviteSerializer(serializers.ModelSerializer):
#     invited_by_email = serializers.ReadOnlyField(source="invited_by.email")

#     class Meta:
#         model = CompanyInvite
#         fields = ["id", "company", "email", "role", "status", "invited_by", "invited_by_email", "created_at", "updated_at"]
#         read_only_fields = ["status", "invited_by", "created_at", "updated_at"]