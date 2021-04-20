from django.utils.encoding import smart_text
from rest_framework.renderers import BaseRenderer


class PDFRenderer(BaseRenderer):
    """PDF Renderer."""

    media_type = "application/pdf"
    format = "pdf"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """Return PDF data as is."""
        if renderer_context is not None:
            if (
                "response" in renderer_context.keys()
                and renderer_context["response"].content_type == "application/json"
            ):
                return
        return data


class PlainTextRenderer(BaseRenderer):
    """Plain text Renderer."""

    media_type = "text/plain"
    format = "txt"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """Return text data as smart text."""
        return smart_text(data, encoding=self.charset)
