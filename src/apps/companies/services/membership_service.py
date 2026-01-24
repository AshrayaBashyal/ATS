from django.core.exceptions import ValidationError
from apps.companies.models import Membership
from django.db import transaction


def change_member_role(*, membership, new_role, changed_by):
    """
    Change role of a member.
    Only admins can change roles.
    Cannot remove last admin.
    """
    with transaction.atomic():
        membership = Membership.objects.select_for_update().get(id=membership.id)

        if membership.role == Membership.Role.ADMIN:
            total_admins = Membership.objects.filter(
                company=membership.company,
                role=Membership.Role.ADMIN
            ).count()

            if total_admins == 1:
                raise ValidationError("Cannot change role of the last admin.")

        membership.role = new_role
        membership.save(update_fields=["role"])
        return membership


def remove_member(*, membership, removed_by):
    """
    Remove a member from company.
    Prevent removing last admin.
    """
    with transaction.atomic():
        membership = Membership.objects.select_for_update().get(id=membership.id)

        if membership.role == Membership.Role.ADMIN:
            total_admins = Membership.objects.filter(
                company=membership.company,
                role=Membership.Role.ADMIN
            ).count()

            if total_admins == 1:
                raise ValidationError("Cannot remove the last admin.")

        membership.delete()