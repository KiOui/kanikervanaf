from django import forms
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from django.conf import settings


class ContactForm(forms.Form):
    """Contact form."""

    name = forms.CharField(label="Naam")
    title = forms.CharField(label="Titel")
    email = forms.EmailField(label="Email adres")
    content = forms.CharField(
        widget=forms.TextInput(attrs={"id": "contact_content"}),
        label="Bericht",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        """Only load captcha on production."""
        super().__init__(*args, **kwargs)
        if settings.RECAPTCHA_PUBLIC_KEY != "" and settings.RECAPTCHA_PRIVATE_KEY != "":
            self.fields["captcha"] = ReCaptchaField(
                widget=ReCaptchaV3(api_params={"hl": "nl"}), label=""
            )
