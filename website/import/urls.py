from django.urls import path
from .views import ImportFromWebsite

urlpatterns = [path("", ImportFromWebsite.as_view(), name="import",)]
