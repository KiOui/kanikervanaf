from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserInformation
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserAdmin(UserAdmin):
    """User admin model for the User object."""

    search_fields = ["email"]

    class Meta:
        """Meta class for the UserAdmin model."""

        model = User


admin.site.register(UserInformation)
admin.site.register(User, CustomUserAdmin)
