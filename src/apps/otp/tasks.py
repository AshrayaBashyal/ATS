from celery import shared_task
from src.apps.emails.services import send_email
from django.contrib.auth import get_user_model
from .services import generate_user_otp

User = get_user_model()

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 10})
def send_otp_email_task(self, user_id: int, purpose: str = "verify"):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return  # Task silently exits

    otp = generate_user_otp(user)

    subject_map = {
        "verify": "Verify your email",
        "login": "Your login OTP",
        "reset": "Reset your password",
    }

    body_map = {
        "verify": "Use this OTP to verify your email.",
        "login": "Use this OTP to complete your login.",
        "reset": "Use this OTP to reset your password.",
    }

    send_email(
        to_email=user.email,
        subject=subject_map.get(purpose, "Your OTP"),
        body=f"{body_map.get(purpose)}\n\nOTP: {otp}\nExpires in 5 minutes.",
    )
