import pyotp

# OTP validity duration (seconds)
OTP_INTERVAL = 300  # 5 minutes


def generate_secret() -> str:
    """
    Generates a long-lived base32 secret.
    Stored on the user model.
    """
    return pyotp.random_base32()


def generate_otp(secret: str) -> str:
    """
    Generate a time-based OTP (TOTP) from a long-lived secret.
    Args:
        secret (str): Base32 encoded OTP secret
    Returns:
        str: 6-digit OTP code
    """
    totp = pyotp.TOTP(secret, interval=OTP_INTERVAL)
    return totp.now()


def verify_otp(secret: str, otp: str) -> bool:
    """
    Verify a provided OTP against a secret.
    Args:
        secret (str): Base32 encoded OTP secret
        otp (str): OTP code provided by user
    Returns:
        bool: True if OTP is valid, False otherwise
    """
    totp = pyotp.TOTP(secret, interval=OTP_INTERVAL)

    # valid_window=1 allows small clock drift (+/- one interval)
    return totp.verify(otp, valid_window=1)
