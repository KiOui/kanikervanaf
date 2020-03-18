"""General views for the website"""

from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = "index.html"
