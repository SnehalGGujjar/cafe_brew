from django.urls import path
from . import views

app_name = "accounts"
urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("otp/", views.otp_view, name="otp"),
    path("change-password/", views.change_password, name="change_password"),
    path("forgot/", views.ForgotPasswordView.as_view(), name="forgot"),
    path("forgot/done/", views.ForgotPasswordDoneView.as_view(), name="forgot_done"),
    path("reset/<uidb64>/<token>/", views.ForgotPasswordConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/complete/", views.ForgotPasswordCompleteView.as_view(), name="forgot_complete"),
]
