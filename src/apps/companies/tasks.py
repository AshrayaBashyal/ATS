from celery import shared_task
from apps.emails.services import send_email
from .models import Invite

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 10})
def send_invite_email_task(self, invite_id: int):
    try:
        # select_related avoids extra DB queries for company details
        invite = Invite.objects.select_related('company').get(id=invite_id)
        
        # invite = CompanyInvite.objects.get(id=invite_id)

    except Invite.DoesNotExist:
        return f"Invite {invite_id} not found."

    subject = f"You are invited to join {invite.company.name}"
    body = (
        f"Hi,\n\n"
        f"You have been invited to join {invite.company.name} as a {invite.role}.\n"
        f"Please log in to your account to accept or reject the invitation.\n\n"
        f"Thanks,\nATS Team"
    )

    # Uses centralized service
    send_email(
        to_email=invite.email,
        subject=subject,
        body=body,
    )