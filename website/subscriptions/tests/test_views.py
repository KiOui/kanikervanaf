import urllib.parse

from django.urls import reverse
from django.test import TestCase
from subscriptions.models import SubscriptionCategory, Subscription


class SubscriptionViews(TestCase):
    fixtures = ["subscriptions.json"]

    def test_overview_view(self):
        response = self.client.get(reverse("subscriptions:overview"), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_overview_category_view(self):
        response = self.client.get(
            reverse(
                "subscriptions:overview_category",
                kwargs={"category": SubscriptionCategory.objects.get(slug="t-mobile")},
            ),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

    def test_overview_category_redirect_view(self):
        response = self.client.get(
            reverse(
                "subscriptions:overview_category_redirect",
                kwargs={
                    "category": SubscriptionCategory.objects.get(slug="t-mobile").id
                },
            ),
            follow=False,
        )
        self.assertEqual(response.status_code, 301)

    def test_overview_category_page_view(self):
        response = self.client.get(
            reverse(
                "subscriptions:overview_category_page",
                kwargs={
                    "category": SubscriptionCategory.objects.get(slug="t-mobile"),
                    "page": 1,
                },
            ),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

    def test_overview_category_page_redirect_view(self):
        response = self.client.get(
            reverse(
                "subscriptions:overview_category_page_redirect",
                kwargs={
                    "category": SubscriptionCategory.objects.get(slug="t-mobile").id,
                    "page": 1,
                },
            ),
            follow=False,
        )
        self.assertEqual(response.status_code, 301)

    def test_summary_view(self):
        response = self.client.get(reverse("subscriptions:summary"), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_send_view(self):
        response_redirect = self.client.get(reverse("subscriptions:send"), follow=False)
        self.assertEqual(response_redirect.status_code, 302)
        self.client.cookies["subscription_details"] = urllib.parse.quote(
            '{"first_name": "something", "email": "something@something.com"}'
        )
        instance = Subscription.objects.get(slug="basic-fit-belgie")
        self.client.cookies["subscription_items"] = urllib.parse.quote(
            '[{"id": ' + str(instance.id) + "}]"
        )
        response_accepted = self.client.get(reverse("subscriptions:send"), follow=False)
        self.assertEqual(
            response_accepted.url, reverse("subscriptions:verification_send_succeeded")
        )
