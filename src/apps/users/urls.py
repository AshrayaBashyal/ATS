from django.urls import path
from .views import (
    RegisterView,
    VerifyEmailView,
    LoginView,
    ForgotPasswordView,
    ResetPasswordView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="user-register"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
    path("login/", LoginView.as_view(), name="user-login"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),
]
