from celery import shared_task
from apps.applications.models import Application
from apps.emails.services import (
    send_application_status_email,
)

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=30, retry_kwargs={"max_retries": 3})
def send_application_status_email_task(self, application_id, to_status):
    application = Application.objects.select_related(
        "candidate", "job__company"
    ).get(id=application_id)

    send_application_status_email(
        application=application,
        to_status=to_status,
    )
