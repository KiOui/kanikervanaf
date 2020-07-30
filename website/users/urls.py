from django.urls import path
from .views import (
    BasicUserInformation,
    LoginView,
    RegisterView,
    ForgotView,
    LogoutView,
    ResetView,
    AccountView,
    EmailConfirmView,
)

urlpatterns = [
    path("enter", BasicUserInformation.as_view(), name="enter",),
    path("login", LoginView.as_view(), name="login"),
    path("logout", LogoutView.as_view(), name="logout"),
    path("register", RegisterView.as_view(), name="register"),
    path("forgot", ForgotView.as_view(), name="forgot"),
    path("reset/<str:token>", ResetView.as_view(), name="reset"),
    path("update/<str:token>", EmailConfirmView.as_view(), name="confirm"),
    path("account", AccountView.as_view(), name="account"),
]
