from django.views.generic import TemplateView


class IndexView(TemplateView):
    """Home view."""

    template_name = "index.html"


class FAQView(TemplateView):
    """Frequently asked questions view."""

    template_name = "faq.html"


class ContactView(TemplateView):
    """Contact view."""

    template_name = "contact.html"
