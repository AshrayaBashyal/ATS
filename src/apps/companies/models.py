from django.db import models
from django.conf import settings
from django.core.validators import EmailValidator


User = settings.AUTH_USER_MODEL

class Company(models.Model):
    name=models.CharField(max_length=250, unique=True)
    description=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    owner=models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_companies")

    def __str__(self):
        return self.name


class CompanyMember(models.Model):
    ADMIN="admin"
    MANAGER="manager"
    RECRUITER="recruiter"
    ROLE_CHOICES=[
        (ADMIN,"Admin"),
        (MANAGER,"Manager"),
        (RECRUITER,"Recruiter")
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="members")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=RECRUITER)
    joined_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "company")


class CompanyInvite(models.Model):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELED = "canceled"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (ACCEPTED, "Accepted"),
        (REJECTED, "Rejected"),
        (CANCELED, "Canceled"),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="invites")
    email = models.EmailField(validators=[EmailValidator()])
    role = models.CharField(max_length=10, choices=CompanyMember.ROLE_CHOICES, default=CompanyMember.RECRUITER)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_invites")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("company", "email")

    def __str__(self):
        return f"Invite {self.email} to {self.company} ({self.status})"    