from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.utils import timezone
import pyotp


class UserManager(BaseUserManager):
    def create_user(
        self,
        email,
        password=None,
        first_name=None,
        middle_name=None,
        last_name=None,
        dob=None,
        **extra_fields
    ):
        if not email:
            raise ValueError("Email is required.")

        if not first_name or not last_name:
            raise ValueError("First and last name are required.")

        # DOB presence rule (only for regular users)
        if not extra_fields.get("is_superuser", False) and not dob:
            raise ValueError("Date of birth is required for regular users.")

        email = self.normalize_email(email)

        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", False)

        user = self.model(
            email=email,
            first_name=first_name.strip(),
            middle_name=middle_name.strip() if middle_name else None,
            last_name=last_name.strip(),
            dob=dob,
            **extra_fields,
        )

        user.set_password(password)

        # Generate OTP secret ONCE (used to derive time-based OTPs)
        if not user.otp_secret:
            user.otp_secret = pyotp.random_base32()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(
            email=email,
            password=password,
            first_name="Admin",
            middle_name=None,
            last_name="User",
            dob=None,
            **extra_fields,
        )