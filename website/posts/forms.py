from django import forms
from .models import Post
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3


class PostForm(forms.ModelForm):
    """Form for posting posts."""

    title = forms.CharField(label="Titel")
    content = forms.CharField(
        widget=forms.TextInput(attrs={"id": "post_content"}),
        label="Bericht",
        required=False,
    )
    captcha = ReCaptchaField(widget=ReCaptchaV3(api_params={"hl": "nl"}), label="")

    class Meta:
        """Meta class for PostForm objects."""

        model = Post
        fields = ["title", "content"]
