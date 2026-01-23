from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from apps.companies.models import Invite, Membership

User = get_user_model()


def send_invite(*, email, company, role, invited_by):
    """
    Send invite to a user.
    Only admins should be allowed (checked in view layer).
    """

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
    """
    User accepts invite.
    Creates membership.
    """

    if invite.status != Invite.Status.PENDING:
        raise ValidationError("Invite is no longer valid.")

    membership, created = Membership.objects.get_or_create(
        user=user,
        company=invite.company,
        defaults={"role": invite.role}
    )

    invite.status = Invite.Status.ACCEPTED
    invite.save(update_fields=["status"])

    return membership


def reject_invite(*, invite):
    invite.status = Invite.Status.REJECTED
    invite.save(update_fields=["status"])


def cancel_invite(*, invite):
    if invite.status != Invite.Status.PENDING:
        raise ValidationError("Only pending invites can be cancelled.")

    invite.status = Invite.Status.CANCELLED
    invite.save(update_fields=["status"])
