from django.views.generic import TemplateView


class BasicUserInformation(TemplateView):
    """View for entering user information."""

    template_name = "enter_information.html"
