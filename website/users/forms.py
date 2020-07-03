from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import UsernameField
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
import random
import string
from .services import send_new_account

User = get_user_model()


class PasswordForgotForm(forms.Form):
    """Form for a forgotten password."""

    email = forms.EmailField(label="Email adres")
    captcha = ReCaptchaField(widget=ReCaptchaV3(api_params={"hl": "nl"}), label="")


class PasswordResetForm(forms.Form):
    """Form for a password reset."""

    password = forms.CharField(widget=forms.PasswordInput, label="Nieuw wachtwoord")
    password2 = forms.CharField(
        widget=forms.PasswordInput, label="Herhaal nieuw wachtwoord"
    )
    captcha = ReCaptchaField(widget=ReCaptchaV3(api_params={"hl": "nl"}), label="")

    def clean(self):
        """
        Check if two passwords are the same.

        :return: the cleaned data
        """
        cleaned_data = super(PasswordResetForm, self).clean()
        if cleaned_data.get("password") != cleaned_data.get("password2"):
            raise forms.ValidationError("De wachtwoorden komen niet overeen")

        return cleaned_data


class UserLoginForm(forms.Form):
    """Form for logging in."""

    username = forms.EmailField(label="Email adres")
    password = forms.CharField(widget=forms.PasswordInput, label="Wachtwoord")
    captcha = ReCaptchaField(widget=ReCaptchaV3(api_params={"hl": "nl"}), label="")

    def clean(self, *args, **kwargs):
        """
        Check if two passwords are the same.

        :return: the cleaned data
        """
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError(
                    "Deze gebruiker bestaat niet of het wachtwoord is incorrect"
                )
            elif not user.is_active:
                raise forms.ValidationError("Deze gebruiker is inactief")
        return super(UserLoginForm, self).clean()


class UserRegisterForm(forms.ModelForm):
    """Form for user registration."""

    email = forms.EmailField(label="Email adres")
    username = forms.CharField(label="Gebruikersnaam")
    password = forms.CharField(widget=forms.PasswordInput, label="Wachtwoord")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Herhaal wachtwoord")
    captcha = ReCaptchaField(widget=ReCaptchaV3(api_params={"hl": "nl"}), label="")

    class Meta:
        """Meta class for user registration."""

        model = User
        fields = ["username", "email", "password", "password2"]

    def clean_email(self):
        """
        Check if email already exists in database.

        :return: cleaned email or ValidationError
        """
        email = self.cleaned_data.get("email")

        email_qs = User.objects.filter(email=email)
        if email_qs.exists():
            raise forms.ValidationError("Dit email-adres bestaat al")

        return email

    def clean_username(self):
        """
        Check if username already exists in database.

        :return: cleaned username or ValidationError
        """
        username = self.cleaned_data.get("username")
        username_qs = User.objects.filter(username=username)
        if username_qs.exists():
            raise forms.ValidationError("Deze gebruikersnaam bestaat al")

        return username

    def clean(self):
        """
        Check if two passwords are the same.

        :return: the cleaned data
        """
        cleaned_data = super(UserRegisterForm, self).clean()
        if cleaned_data.get("password") != cleaned_data.get("password2"):
            raise forms.ValidationError("De wachtwoorden komen niet overeen")

        return cleaned_data


class BackendUserCreationForm(forms.ModelForm):
    """Form to create a user with a random password and send an email."""

    class Meta:
        """Meta class for BackendUserCreationForm."""

        model = User
        fields = [
            "username",
            "email",
            "first_name",
        ]
        field_classes = {
            "username": UsernameField,
            "email": forms.CharField,
            "first_name": forms.CharField,
        }
        help_texts = {
            "email": "Let op! Er zal na het aanmaken van het account direct een email worden verstuurd naar "
            "het email adres wat hier is opgegeven met daarin het wachtwoord en de gebruikersnaam."
        }

    def save(self, commit=True):
        """
        Generate a random password and send an email.

        :param commit whether to commit or not
        :return: the created user
        """
        user = super().save(commit=False)
        password = self.generate_random_password()
        user.set_password(password)
        send_new_account(user, password)
        if commit:
            user.save()

        return user

    @staticmethod
    def generate_random_password():
        """
        Generate a random password.

        :return: a random 16 character password
        """
        return "".join(
            random.choice(string.ascii_letters + string.digits) for x in range(16)
        )


class PasswordUpdateForm(forms.Form):
    """Update user password form."""

    oldpassword = forms.CharField(widget=forms.PasswordInput, label="Oud wachtwoord")
    password = forms.CharField(widget=forms.PasswordInput, label="Wachtwoord")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Herhaal wachtwoord")
    captcha = ReCaptchaField(widget=ReCaptchaV3(api_params={"hl": "nl"}), label="")

    def clean(self):
        """
        Check if two passwords are the same and if the old password is not equal to the new password.

        :return: the cleaned data
        """
        cleaned_data = super(PasswordUpdateForm, self).clean()
        if cleaned_data.get("password") != cleaned_data.get("password2"):
            raise forms.ValidationError("De wachtwoorden komen niet overeen")
        elif cleaned_data.get("password") == cleaned_data.get("oldpassword"):
            raise forms.ValidationError(
                "Het nieuwe wachtwoord moet anders zijn dan het oude wachtwoord"
            )

        return cleaned_data


class EnterUserInformationForm(forms.Form):
    """Enter user information form."""

    email = forms.EmailField(
        label="Uw e-mail",
        required=True,
        widget=forms.EmailInput(attrs={"id": "email", "class": "container-fluid"}),
    )
    first_name = forms.CharField(
        label="Voornaam",
        required=True,
        widget=forms.TextInput(attrs={"id": "firstname", "class": "container-fluid"}),
    )
    last_name = forms.CharField(
        label="Achternaam",
        required=False,
        widget=forms.TextInput(attrs={"id": "lastname", "class": "container-fluid"}),
    )
    address = forms.CharField(
        label="Adres",
        required=False,
        widget=forms.TextInput(attrs={"id": "address", "class": "container-fluid"}),
    )
    postal_code = forms.CharField(
        label="Postcode",
        required=False,
        widget=forms.TextInput(attrs={"id": "postalcode", "class": "container-fluid"}),
    )
    residence = forms.CharField(
        label="Woonplaats",
        required=False,
        widget=forms.TextInput(attrs={"id": "residence", "class": "container-fluid"}),
    )

    def __init__(self, *args, **kwargs):
        """
        Initialize enter userinformation form.

        :param args: arguments
        :param kwargs: keyword arguments, if this includes the "user" keyword argument the field will be preset to the
        user
        """
        user = kwargs.pop("user", None)
        if user is not None:
            initial = kwargs.get("initial", {})
            user_information = {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "address": user.get_profile().address,
                "postal_code": user.get_profile().postal_code,
                "residence": user.get_profile().residence,
            }
            user_information.update(initial)
            kwargs.update(initial=user_information)
        super(EnterUserInformationForm, self).__init__(*args, **kwargs)


class UserUpdateForm(forms.Form):
    """Update user information form."""

    first_name = forms.CharField(label="Voornaam", required=False)
    last_name = forms.CharField(label="Achternaam", required=False)
    address = forms.CharField(label="Adres", required=False)
    postal_code = forms.CharField(label="Postcode", required=False)
    residence = forms.CharField(label="Woonplaats", required=False)
    captcha = ReCaptchaField(widget=ReCaptchaV3(api_params={"hl": "nl"}), label="")

    def __init__(self, *args, **kwargs):
        """
        Initialize user update form.

        :param args: arguments
        :param kwargs: keyword arguments, if this includes the "user" keyword argument the field will be preset to the
        user
        """
        user = kwargs.pop("user", None)
        if user is not None:
            initial = kwargs.get("initial", {})
            user_information = {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "address": user.get_profile().address,
                "postal_code": user.get_profile().postal_code,
                "residence": user.get_profile().residence,
            }
            user_information.update(initial)
            kwargs.update(initial=user_information)
        super(UserUpdateForm, self).__init__(*args, **kwargs)
