from django.urls import reverse
from django.test import TestCase
from django.core import mail


class KanikervanafViews(TestCase):
    def test_home_view(self):
        response = self.client.get(reverse("home"), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_faq_view(self):
        response = self.client.get(reverse("faq"), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_privacy_view(self):
        response = self.client.get(reverse("privacy"), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_contact_view(self):
        response = self.client.get(reverse("contact"), follow=True)
        self.assertEqual(response.status_code, 200)
        response_post = self.client.post(
            reverse("contact"),
            data={
                "name": "Test name",
                "email": "something@something.com",
                "title": "Test title",
            },
        )
        self.assertEqual(response_post.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)

    def test_sitemap_view(self):
        response = self.client.get(
            reverse("django.contrib.sitemaps.views.sitemap"), follow=True
        )
        self.assertEqual(response.status_code, 200)
