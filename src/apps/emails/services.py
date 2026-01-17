from django.core.mail import send_mail
from django.conf import settings

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
