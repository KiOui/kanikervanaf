from django import forms
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3


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
    captcha = ReCaptchaField(widget=ReCaptchaV3(api_params={"hl": "nl"}), label="")
