from django.views.generic import TemplateView


class IndexView(TemplateView):
    """Home view."""

    template_name = "index.html"
