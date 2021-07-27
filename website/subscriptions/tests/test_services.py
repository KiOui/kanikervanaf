from django.test import TestCase
from django.template.exceptions import TemplateSyntaxError
from subscriptions.services import render_string, handle_verification_request, store_subscription_list
from subscriptions.models import Subscription, QueuedMailList


class SubscriptionServices(TestCase):
    fixtures = ["subscriptions.json"]

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

    def test_handle_verification_request(self):
        test_deregister_subscriptions = [{"id": x} for x in [
            Subscription.objects.get(slug="t-mobile-data").id,
            Subscription.objects.get(slug="fit-for-free-france").id,
            Subscription.objects.get(slug="the-guardian").id,
        ]]
        self.assertIsInstance(handle_verification_request(
            {
                "first_name": "First name test",
                "second_name": "Second name test",
                "email": "test@test.com",
                "address": "Test address",
                "postal_code": "1111AA",
                "residence": "Test city",
            },
            test_deregister_subscriptions,
        ), QueuedMailList)
        self.assertFalse(handle_verification_request(
            {
                "second_name": "Second name test",
                "email": "test@test.com",
                "address": "Test address",
                "postal_code": "1111AA",
                "residence": "Test city",
            },
            test_deregister_subscriptions
        ))
        self.assertFalse(handle_verification_request({
                "first_name": "First name test",
                "second_name": "Second name test",
                "address": "Test address",
                "postal_code": "1111AA",
                "residence": "Test city",},
        test_deregister_subscriptions)
        )

    def test_store_subscription_list(self):
        test_subscription_list = [
            Subscription.objects.get(slug="t-mobile-data"),
            Subscription.objects.get(slug="fit-for-free-france"),
            Subscription.objects.get(slug="the-guardian"),
        ]
        test_subscription_items_list = [{"id": x.id} for x in test_subscription_list]
        test_subscription_items_list_with_fakes = [{"id": Subscription.objects.get(slug="t-mobile-data")}, {"something-else": "something-different"}, {"id": -5}]
        self.assertCountEqual(store_subscription_list(test_subscription_items_list), set(test_subscription_list))
