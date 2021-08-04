import urllib.parse

from django.urls import reverse
from django.core import mail
from django.test import TestCase
from django.contrib.auth import get_user_model
from subscriptions.models import SubscriptionCategory, Subscription, QueuedMailList

User = get_user_model()


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

    def test_request_view(self):
        response = self.client.get(reverse("subscriptions:request"), follow=True)
        self.assertEqual(response.status_code, 200)
        response_post = self.client.post(
            reverse("subscriptions:request"),
            data={
                "name": "Test name",
                "email": "something@something.com",
                "subscription_name": "Test subscription",
            },
        )
        self.assertEqual(response_post.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)

    def test_details_search_view(self):
        response = self.client.get(reverse("subscriptions:details_search"), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_details_view(self):
        response = self.client.get(
            reverse(
                "subscriptions:details",
                kwargs={
                    "subscription": Subscription.objects.get(
                        slug="basic-fit-netherlands"
                    )
                },
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_details_redirect_view(self):
        response = self.client.get(
            reverse(
                "subscriptions:details_redirect",
                kwargs={
                    "subscription": Subscription.objects.get(
                        slug="basic-fit-netherlands"
                    ).id
                },
            )
        )
        self.assertEqual(response.status_code, 301)

    def test_verify_view(self):
        response = self.client.get(
            reverse("subscriptions:verify", kwargs={"token": "abcd"})
        )
        self.assertEqual(response.status_code, 404)
        generated_mail_list = QueuedMailList.generate(
            "First name",
            "Second name",
            "something@something.com",
            "Test address 1",
            "1111AA",
            "Somewhere",
            [Subscription.objects.get(slug="basic-fit-netherlands")],
        )
        response_exists = self.client.get(
            reverse("subscriptions:verify", kwargs={"token": generated_mail_list.token})
        )
        self.assertEqual(response_exists.status_code, 200)

    def test_verification_send_succeeded_view(self):
        response = self.client.get(reverse("subscriptions:verification_send_succeeded"))
        self.assertEqual(response.status_code, 200)

    def test_verification_send_failed_view(self):
        response = self.client.get(reverse("subscriptions:verification_send_failed"))
        self.assertEqual(response.status_code, 200)

    def test_admin_template_information_view(self):
        admin_user = User.objects.create_user("test", "test@test.com", "password")
        admin_user.is_staff = True
        admin_user.save()
        response_unauthorized = self.client.get(
            reverse("subscriptions:admin_template_information")
        )
        self.assertEqual(response_unauthorized.status_code, 403)
        self.client.login(username="test@test.com", password="password")
        response_authorized = self.client.get(
            reverse("subscriptions:admin_template_information")
        )
        self.assertEqual(response_authorized.status_code, 200)

    def test_basic_user_information_view(self):
        response = self.client.get(reverse("subscriptions:enter"))
        self.assertEqual(response.status_code, 200)
