from django.urls import path
from .views import BasicUserInformation

urlpatterns = [
    path("enter", BasicUserInformation.as_view(), name="enter",),
]
