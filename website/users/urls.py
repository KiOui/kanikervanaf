from django.urls import path
from .views import (
    BasicUserInformation,
    LoginView,
    RegisterView,
    ForgotView,
    LogoutView,
    ResetView,
)

urlpatterns = [
    path("enter", BasicUserInformation.as_view(), name="enter",),
    path("login", LoginView.as_view(), name="login"),
    path("logout", LogoutView.as_view(), name="logout"),
    path("register", RegisterView.as_view(), name="register"),
    path("forgot", ForgotView.as_view(), name="forgot"),
    path("reset/<str:token>", ResetView.as_view(), name="reset"),
]
