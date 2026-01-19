from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    OTPVerifySerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    UserSerializer,
)
from .models import User

from apps.otp.services import verify_user_otp, clear_user_otp
from apps.otp.tasks import send_otp_email_task



class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        # Send verification OTP
        send_otp_email_task.delay(user.id, purpose="verify")

        return Response(
            {"msg": "User registered. Check your email for OTP verification."},
            status=status.HTTP_201_CREATED,
        )
