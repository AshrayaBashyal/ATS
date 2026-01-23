from django.db import models
from django.conf import settings
from .company import Company
from .membership import Membership


class Invite(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"

    email = models.EmailField()

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="invites"
    )

    role = models.CharField(
        max_length=20,
        choices=Membership.Role.choices
    )

    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_invites"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("email", "company", "status")

    def __str__(self):
        return f"{self.email} invited to {self.company.name} as {self.role}"
