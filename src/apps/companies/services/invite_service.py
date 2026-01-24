from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from apps.companies.models import Invite, Membership

User = get_user_model()


def send_invite(*, email, company, role, invited_by):
    """
    Send invite to a user.
    Only admins should be allowed (checked in view layer).
    """
    if Membership.objects.filter(user__email=email, company=company).exists():
        raise ValidationError("User already in company.")

    if Invite.objects.filter(
        email=email,
        company=company,
        status=Invite.Status.PENDING
    ).exists():
        raise ValidationError("Pending invite already exists.")

    invite = Invite.objects.create(
        email=email,
        company=company,
        role=role,
        invited_by=invited_by
    )

    return invite


def accept_invite(*, invite, user):

    if invite.status != Invite.Status.PENDING:
        raise ValidationError("Invite is no longer valid.")

    if invite.email.lower() != user.email.lower():
        raise ValidationError("This invite is not for your account.")

    if Membership.objects.filter(user=user, company=invite.company).exists():
        raise ValidationError("Already a member of this company.")

    membership = Membership.objects.create(
        user=user,
        company=invite.company,
        role=invite.role
    )

    invite.status = Invite.Status.ACCEPTED
    invite.save(update_fields=["status"])

    return membership



def reject_invite(*, invite, user):
    """
    User rejects invite.
    """

    if invite.status != Invite.Status.PENDING:
        raise ValidationError("Invite already processed.")

    if invite.email.lower() != user.email.lower():
        raise ValidationError("This invite is not assigned to your account.")

    invite.status = Invite.Status.REJECTED
    invite.save(update_fields=["status"])


def cancel_invite(*, invite):
    if invite.status != Invite.Status.PENDING:
        raise ValidationError("Only pending invites can be cancelled.")

    invite.status = Invite.Status.CANCELLED
    invite.save(update_fields=["status"])
