from rest_framework.permissions import BasePermission
from apps.companies.models import Membership


class IsCompanyAdmin(BasePermission):
    def has_permission(self, request, view):
        company_id = view.kwargs.get("company_id")
        return Membership.objects.filter(
            company_id=company_id,
            user=request.user,
            role=Membership.Role.ADMIN
        ).exists()
