from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from apps.companies.models import Company, Membership, Invite
from apps.companies.services.company_service import create_company
from apps.companies.services.invite_service import (
    send_invite, accept_invite, reject_invite, cancel_invite, list_user_invites, list_sent_invites
)
from apps.companies.services.membership_service import (
    change_member_role, remove_member
)

from .serializers import *
from .permissions import IsCompanyAdmin


class CompanyCreateView(GenericAPIView):
    serializer_class = CompanyCreateSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
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


class SendInviteView(GenericAPIView):
    serializer_class = SendInviteSerializer
    permission_classes = [IsCompanyAdmin]

    def post(self, request, company_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        company = get_object_or_404(Company, id=company_id)

        invite = send_invite(
            email=serializer.validated_data["email"],
            company=company,
            role=serializer.validated_data["role"],
            invited_by=request.user
        )

        return Response(InviteSerializer(invite).data, status=201)


class AcceptInviteView(APIView):
    def post(self, request, invite_id):
        invite = get_object_or_404(Invite, id=invite_id)
        accept_invite(invite=invite, user=request.user)
        return Response({"detail": "Joined company"})


class RejectInviteView(APIView):
    def post(self, request, invite_id):
        invite = get_object_or_404(Invite, id=invite_id)
        reject_invite(invite=invite, user=request.user)
        return Response({"detail": "Invite rejected"})


class ChangeRoleView(GenericAPIView):
    serializer_class = ChangeRoleSerializer
    permission_classes = [IsCompanyAdmin]

    def post(self, request, membership_id):
        membership = get_object_or_404(Membership, id=membership_id)
        serializer = self.get_serializer(data=request.data)
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
        try:
            remove_member(membership=membership, removed_by=request.user)
        except ValidationError as e:
            # Return a clean JSON response with the error message
            return Response(
                {"detail": e.messages},  # e.messages is a list
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


# class MyInvitesView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user

#         # # Invites I received
#         # received_invites = Invite.objects.filter(
#         #     email__iexact=user.email,
#         #     status=Invite.Status.PENDING
#         # ).select_related("company", "invited_by")

#         # # Invites I sent
#         # sent_invites = Invite.objects.filter(
#         #     invited_by=user
#         # ).select_related("company", "invited_by")

#         # Use service functions
#         received_invites = list_user_invites(user=user)
#         sent_invites = list_sent_invites(user=user)

#         data = {
#             "received": MyInviteSerializer(received_invites, many=True).data,
#             "sent": MyInviteSerializer(sent_invites, many=True).data
#         }

#         return Response(data)



class MyInvitesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Invites received (pending)
        received_invites = Invite.objects.filter(
            email__iexact=user.email,
            status=Invite.Status.PENDING
        ).select_related("company", "invited_by")

        # Invites sent by this user
        sent_invites = Invite.objects.filter(
            invited_by=user
        ).select_related("company", "invited_by")

        data = {
            "received": MyInviteSerializer(received_invites, many=True).data,
            "sent": MyInviteSerializer(sent_invites, many=True).data
        }

        return Response(data)


class CancelInviteView(APIView):
    permission_classes = [IsCompanyAdmin]

    def post(self, request, invite_id):
        invite = get_object_or_404(Invite, id=invite_id)
        cancel_invite(invite=invite, cancelled_by=request.user)
        return Response({"detail": "Invite cancelled"})