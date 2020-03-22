from django.urls import path
from .views import verify, VerificationSendFailed, VerificationSendSucceeded

urlpatterns = [
    path("verify/<str:token>", verify, name="verify",),
    path(
        "verification-request/succeeded",
        VerificationSendSucceeded.as_view(),
        name="verification_send_succeeded",
    ),
    path(
        "verification-request/failed",
        VerificationSendFailed.as_view(),
        name="verification_send_failed",
    ),
]
