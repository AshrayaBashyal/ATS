from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from apps.companies.models import Company, Membership, Invite
from apps.companies.services.company_service import create_company
from apps.companies.services.invite_service import (
    send_invite, accept_invite, reject_invite, cancel_invite
)
from apps.companies.services.membership_service import (
    change_member_role, remove_member
)

from .serializers import *
from .permissions import IsCompanyAdmin


class CompanyCreateView(APIView):
    def post(self, request):
        serializer = CompanyCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        company = create_company(
            name=serializer.validated_data["name"],
            description=serializer.validated_data["description"],
            created_by=request.user
        )

        return Response(CompanySerializer(company).data, status=201)


class MyCompaniesView(APIView):
    def get(self, request):
        companies = Company.objects.filter(memberships__user=request.user)
        return Response(CompanySerializer(companies, many=True).data)


class CompanyMembersView(APIView):
    def get(self, request, company_id):
        members = Membership.objects.filter(company_id=company_id)
        return Response(MembershipSerializer(members, many=True).data)


class SendInviteView(APIView):
    permission_classes = [IsCompanyAdmin]

    def post(self, request, company_id):
        serializer = SendInviteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        company = get_object_or_404(Company, id=company_id)

        invite = send_invite(
            email=serializer.validated_data["email"],
            company=company,
            role=serializer.validated_data["role"],
            invited_by=request.user
        )

        return Response(InviteSerializer(invite).data)


class AcceptInviteView(APIView):
    def post(self, request, invite_id):
        invite = get_object_or_404(Invite, id=invite_id, email=request.user.email)
        membership = accept_invite(invite=invite, user=request.user)
        return Response({"detail": "Joined company"})


class RejectInviteView(APIView):
    def post(self, request, invite_id):
        invite = get_object_or_404(Invite, id=invite_id, email=request.user.email)
        reject_invite(invite=invite)
        return Response({"detail": "Invite rejected"})


class ChangeRoleView(APIView):
    permission_classes = [IsCompanyAdmin]

    def post(self, request, membership_id):
        membership = get_object_or_404(Membership, id=membership_id)
        serializer = ChangeRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        change_member_role(
            membership=membership,
            new_role=serializer.validated_data["role"],
            changed_by=request.user
        )

        return Response({"detail": "Role updated"})


class RemoveMemberView(APIView):
    permission_classes = [IsCompanyAdmin]

    def delete(self, request, membership_id):
        membership = get_object_or_404(Membership, id=membership_id)
        remove_member(membership=membership, removed_by=request.user)
        return Response(status=204)
