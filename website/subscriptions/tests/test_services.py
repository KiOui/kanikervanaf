from django.test import TestCase
from django.template.exceptions import TemplateSyntaxError
from subscriptions.services import render_string


class SubscriptionServices(TestCase):
    def test_render_string(self):
        without_django_engine = (
            "This is a line of text, you can insert your name here: {{ name }}."
        )
        with_django_engine = "{% load static %}By loading static we test whether we are rendering with or without the Django engine."
        self.assertEquals(
            render_string(without_django_engine, {"name": "Test name"}),
            "This is a line of text, you can insert your name here: Test name.",
        )
        self.assertEquals(
            render_string(with_django_engine, {}, use_django_engine=True),
            "By loading static we test whether we are rendering with or without the Django engine.",
        )
        with self.assertRaisesMessage(
            TemplateSyntaxError,
            "'static' is not a registered tag library. Must be one of:",
        ):
            render_string(with_django_engine, {"name": "Test name"})
