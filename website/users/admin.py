from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserInformation
from django.contrib.auth import get_user_model
from .forms import BackendUserCreationForm

User = get_user_model()


class CustomUserAdmin(UserAdmin):
    """User admin model for the User object."""

    add_form = BackendUserCreationForm
    search_fields = ["email"]

    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("username", "email", "first_name"),}),
    )

    class Meta:
        """Meta class for the CustomUserAdmin model."""

        model = User


admin.site.register(User, CustomUserAdmin)
