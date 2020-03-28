from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout

from .forms import (
    UserLoginForm,
    UserRegisterForm,
    PasswordForgotForm,
    PasswordResetForm,
    UserUpdateForm,
)
from .models import User, PasswordReset
from .services import generate_password_reset, send_reset_password


class BasicUserInformation(TemplateView):
    """View for entering user information."""

    template_name = "enter_information.html"


class LoginView(TemplateView):
    """View for logging in."""

    template_name = "login.html"

    def get(self, request, **kwargs):
        """
        GET request for login view.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the login page or a redirect to the next parameter or home page
        """
        next_page = request.GET.get("next")
        if request.user.is_authenticated:
            if next_page:
                return redirect(next_page)
            return redirect("/")

        form = UserLoginForm(None)
        context = {"form": form}
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        """
        POST request for login view.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the login page or a redirect to next or the home page
        """
        next_page = request.GET.get("next")
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            login(request, user)
            if next_page:
                return redirect(next_page)
            return redirect("/")
        context = {"form": form}
        return render(request, self.template_name, context)


class RegisterView(TemplateView):
    """Registration view."""

    template_name = "register.html"

    def get(self, request, **kwargs):
        """
        GET request for registration view.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the registration page or a redirect to the next parameter or home page
        """
        next_page = request.GET.get("next")
        if request.user.is_authenticated:
            if next_page:
                return redirect(next_page)
            return redirect("/")

        form = UserRegisterForm(None)
        context = {"form": form}
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        """
        POST request for registration view.

        This function registers a new user
        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the registration page
        """
        if request.user.is_authenticated:
            return redirect("/")

        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get("password")
            user.set_password(password)
            user.save()
            print(user)
            new_user = authenticate(username=user.email, password=password)
            print(new_user)
            login(request, new_user)
            return render(request, self.template_name, {"succeeded": True})

        context = {"form": form}

        return render(request, self.template_name, context)


class ForgotView(TemplateView):
    """Forgot password view."""

    template_name = "forgot.html"

    def get(self, request, **kwargs):
        """
        GET request for forgot password view.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the forgot password page
        """
        form = PasswordForgotForm(None)
        context = {"form": form}
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        """
        POST request for login view.

        This function generates a PasswordReset object and sends a password reset email
        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the forgot password page
        """
        form = PasswordForgotForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                reset = generate_password_reset(user)
                send_reset_password(reset, request)
            return render(request, self.template_name, {"succeeded": True})
        context = {"form": form}
        return render(request, self.template_name, context)


class LogoutView(TemplateView):
    """Log out view."""

    template_name = "logout.html"

    def get(self, request, **kwargs):
        """
        GET request for logout view.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the logout page or a redirect to the next parameter or home page
        """
        next_page = request.GET.get("next")
        if request.user.is_authenticated:
            logout(request)
            if next_page:
                return redirect(next_page)
            return render(request, self.template_name)
        else:
            if next_page:
                return redirect(next_page)
            return redirect("/")


class ResetView(TemplateView):
    """Reset password view."""

    template_name = "reset.html"

    def get(self, request, **kwargs):
        """
        GET request for reset password view.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the reset password page
        """
        form = PasswordResetForm(None)
        context = {"form": form}
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        """
        POST request for reset password view.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the reset password page
        """
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data.get("password")
            token = kwargs.get("token")
            if PasswordReset.objects.filter(token=token).exists():
                PasswordReset.remove_expired()
                reset = PasswordReset.objects.get(token=token)
                reset.user.set_password(new_password)
                reset.user.save()
                reset.delete()
                return render(request, self.template_name, {"succeeded": True})
            else:
                return render(request, self.template_name, {"failed": True})

        context = {"form": form}
        return render(request, self.template_name, context)


class AccountView(LoginRequiredMixin, TemplateView):
    """Account details page, requires logged in user."""

    template_name = "account.html"

    def get(self, request, **kwargs):
        """
        GET method for account details page.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the accounts page with initial information filled in
        """
        initial = {}
        form = UserUpdateForm(initial=initial)

        context = {"form": form}

        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        """
        POST method for account details page.

        Changes details of a user account
        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the accounts page
        """
        form = UserUpdateForm(request.POST)

        context = {"form": form}

        if form.is_valid():
            if request.user.check_password(form.cleaned_data.get("oldpassword")):
                request.user.set_password(form.cleaned_data.get("password"))
                request.user.save()
                context["succeeded"] = True
                return render(request, self.template_name, context)
            else:
                context["failed"] = True
                return render(request, self.template_name, context)

        return render(request, self.template_name, context)
