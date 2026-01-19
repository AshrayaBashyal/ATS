from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import (
    RegisterSerializer, LoginSerializer, OTPVerifySerializer,
    ForgotPasswordSerializer, ResetPasswordSerializer, UserSerializer
)
from apps.emails.services import send_verification_email_task, send_reset_password_email_task
from apps.otp.utils import verify_otp
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from django.shortcuts import get_object_or_404


def _verify_user_otp(user, otp):
    """Helper to verify OTP and clear it if valid"""
    if verify_otp(user.otp_secret, otp):
        user.otp_secret = None
        return True
    return False


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        send_verification_email_task.delay(user.id)
        return user

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response(
            {"msg": "User registered. Check your email for OTP verification."},
            status=status.HTTP_201_CREATED
        )


class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    pagination_class = None  # We'll add DRF pagination later


class VerifyEmailView(generics.GenericAPIView):
    serializer_class = OTPVerifySerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        user = get_object_or_404(User, email=email)

        if _verify_user_otp(user, otp):
            user.is_verified = True
            user.save()
            return Response({"msg": "Email verified successfully."})
        return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = authenticate(request, email=email, password=password)
        if not user:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_verified:
            return Response({"error": "Email not verified"}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })


class ForgotPasswordView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Prevent email enumeration
            return Response({"msg": "If the email exists, an OTP was sent."})

        if not user.is_verified:
            return Response({"error": "Email not verified"}, status=status.HTTP_403_FORBIDDEN)

        send_reset_password_email_task.delay(email)
        return Response({"msg": "OTP sent to your email for password reset."})


class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]
        new_password = serializer.validated_data["password"]

        user = get_object_or_404(User, email=email)

        if _verify_user_otp(user, otp):
            user.set_password(new_password)
            user.save()
            return Response({"msg": "Password reset successfully."})
        return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
