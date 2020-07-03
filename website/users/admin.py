from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .forms import BackendUserCreationForm
from .models import Profile

User = get_user_model()


class ProfileInline(admin.StackedInline):
    """Profile inline."""

    template = "admin/edit_inline/stacked_no_header.html"
    model = Profile
    verbose_name_plural = "Profile"


class CustomUserAdmin(UserAdmin):
    """User admin model for the User object."""

    add_form = BackendUserCreationForm
    search_fields = ["email"]

    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("username", "email", "first_name"),}),
    )
    inlines = (ProfileInline,)

    class Meta:
        """Meta class for the CustomUserAdmin model."""

        model = User


admin.site.register(User, CustomUserAdmin)
