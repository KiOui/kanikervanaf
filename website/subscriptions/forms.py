from django import forms
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from django.conf import settings


class RequestForm(forms.Form):
    """Subscription request form."""

    subscription_name = forms.CharField(label="Naam van het abonnement")
    name = forms.CharField(label="Uw naam")
    email = forms.EmailField(label="Uw email adres")
    content = forms.CharField(
        widget=forms.TextInput(attrs={"id": "request_content"}),
        label="Eventuele opmerkingen",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        """Only load captcha on production."""
        super().__init__(*args, **kwargs)
        if settings.RECAPTCHA_PUBLIC_KEY != "" and settings.RECAPTCHA_PRIVATE_KEY != "":
            self.fields["captcha"] = ReCaptchaField(
                widget=ReCaptchaV3(api_params={"hl": "nl"}), label=""
            )


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
