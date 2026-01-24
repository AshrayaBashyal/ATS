from rest_framework.permissions import BasePermission
from apps.companies.models import Membership


class IsCompanyAdmin(BasePermission):

    def has_permission(self, request, view):
        company_id = view.kwargs.get("company_id")
        membership_id = view.kwargs.get("membership_id")

        if company_id:
            return Membership.objects.filter(
                company_id=company_id,
                user=request.user,
                role=Membership.Role.ADMIN
            ).exists()

        if membership_id:
            from apps.companies.models import Membership
            membership = Membership.objects.filter(id=membership_id).first()
            if not membership:
                return False
            return Membership.objects.filter(
                company=membership.company,
                user=request.user,
                role=Membership.Role.ADMIN
            ).exists()

        return False
