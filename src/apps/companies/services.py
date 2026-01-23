# from django.core.exceptions import ValidationError, PermissionDenied
# from django.contrib.auth import get_user_model
# from .models import Company, CompanyMember, CompanyInvite

# User = get_user_model()


# class CompanyService:

#     @staticmethod
#     def create_company(owner, name, description=""):
#         company = Company.objects.create(owner=owner, name=name, description=description)
#         # Owner is automatically admin
#         CompanyMember.objects.create(user=owner, company=company, role=CompanyMember.ADMIN)
#         return company
        

#     @staticmethod
#     def add_member(company, user, role, acting_user):
#         # Only admins can add members
#         if not CompanyMember.objects.filter(company=company, user=acting_user, role=CompanyMember.ADMIN).exists():
#             raise PermissionDenied("Only admins can add members")
#         member, created = CompanyMember.objects.get_or_create(user=user, company=company, defaults={"role": role})
#         if not created:
#             member.role = role
#             member.save()
#         return member        
    

#     @staticmethod
#     def send_invite(company, email, role, invited_by):
#         # Only admins can invite
#         if not CompanyMember.objects.filter(company=company, user=invited_by, role=CompanyMember.ADMIN).exists():
#             raise PermissionDenied("Only admins can invite members")
#         invite, created = CompanyInvite.objects.get_or_create(
#             company=company, email=email,
#             defaults={"role": role, "invited_by": invited_by}
#         )
#         if not created:
#             if invite.status in [CompanyInvite.PENDING]:
#                 raise ValidationError("Invite already pending")
#             invite.status = CompanyInvite.PENDING
#             invite.role = role
#             invite.invited_by = invited_by
#             invite.save()
#         return invite    