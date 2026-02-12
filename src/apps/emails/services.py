from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


def send_email(to_email: str, subject: str, body: str, from_email: str = None):
    """
    Sends an email using Django's email backend.
    
    Parameters:
        to_email (str): recipient email
        subject (str): email subject
        body (str): email body text
        from_email (str, optional): sender email. Defaults to settings.DEFAULT_FROM_EMAIL
    """
    from_email = from_email or getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com")

    send_mail(
        subject=subject,
        message=body,
        from_email=from_email,
        recipient_list=[to_email],
        fail_silently=False,  # Raise errors in development; can set True in prod if needed
    )





def send_application_status_email(*, application, to_status):
    """
    Sends candidate-facing emails for certain application statuses.
    """

    candidate = application.candidate
    job = application.job
    company = job.company

    # Only certain statuses trigger emails
    TEMPLATE_MAP = {
        "INTERVIEW": "templates/applications/interview_email.txt",
        "REJECTED": "templates/applications/rejection_email.txt",
        "HIRED": "templates/applications/hired_email.txt",
    }

    template = TEMPLATE_MAP.get(to_status)
    if not template:
        return  # Silent no-op (important)

    context = {
        "candidate_name": candidate.get_full_name() or candidate.email,
        "job_title": job.title,
        "company_name": company.name,
    }

    body = render_to_string(template, context)

    send_mail(
        subject=f"Update on your application for {job.title}",
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[candidate.email],
        fail_silently=False,
    )