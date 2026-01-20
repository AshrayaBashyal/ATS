from django.core.exceptions import ValidationError, PermissionDenied
from django.contrib.auth import get_user_model
from .models import Company, CompanyMember, CompanyInvite

User = get_user_model()


class CompanyService:

    @staticmethod
    def create_company(owner, name, description=""):
        company = Company.objects.create(owner=owner, name=name, description=description)
        # Owner is automatically admin
        CompanyMember.objects.create(user=owner, company=company, role=CompanyMember.ADMIN)
        return company
        