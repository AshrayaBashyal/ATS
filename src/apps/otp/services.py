from apps.users.models import User
from .utils import generate_secret, generate_otp, verify_otp


def ensure_user_secret(user: User) -> None:
    """
    Ensure user has a long-lived OTP secret.
    """
    if not user.otp_secret:
        user.otp_secret = generate_secret()
        user.save(update_fields=["otp_secret"])


def generate_user_otp(user: User, purpose: str = "verify") -> str:
    """
    Generates OTP for a user (verification, reset, etc.)
    """
    ensure_user_secret(user)
    return generate_otp(user.otp_secret)


def verify_user_otp(user: User, otp: str, purpose: str = "verify") -> bool:
    """
    Verifies OTP for a given purpose.
    """
    return verify_otp(user.otp_secret, otp)


def clear_user_otp(user: User) -> None:
    """
    Clears OTP secret after successful usage (optional).
    Useful for one-time flows like password reset.
    """
    user.otp_secret = None
    user.save(update_fields=["otp_secret"])
