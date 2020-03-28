from django import forms
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3


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
    captcha = ReCaptchaField(widget=ReCaptchaV3(api_params={"hl": "nl"}), label="")
