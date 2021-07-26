from django.test import TestCase

from subscriptions.models import (
    Subscription,
    SubscriptionObject,
    SubscriptionCategory,
    SubscriptionSearchTerm,
)
from django.core.files import File
from django.conf import settings

from mock import MagicMock


class SubscriptionObjectTest(TestCase):
    fixtures = ["subscriptions.json"]

    @classmethod
    def setUpTestData(cls):
        cls.mocked_letter_template = MagicMock(spec=File)
        cls.subscription_mocked_letter_template = Subscription.objects.get(
            slug="basic-fit-belgie"
        )

    def test_upload_file(self):
        mocked_letter_template = MagicMock(spec=File)
        mocked_letter_template.name = "letter-template.html"
        subscription_mocked_letter_template = Subscription.objects.get(
            slug="basic-fit-belgie"
        )
        subscription_mocked_letter_template.letter_template = mocked_letter_template
        print(subscription_mocked_letter_template.letter_template_full_path)


class SubscriptionTest(TestCase):
    fixtures = ["subscriptions.json"]

    def test_can_email(self):
        cant_generate_mail = Subscription.objects.get(slug="att-mobile")
        can_generate_mail = Subscription.objects.get(slug="att-data")
        self.assertFalse(cant_generate_mail.can_email())
        self.assertTrue(can_generate_mail.can_email())

    def test_can_letter(self):
        cant_generate_letter = Subscription.objects.get(slug="att-mobile")
        can_generate_letter_support_address = Subscription.objects.get(
            slug="basic-fit-belgie"
        )
        can_generate_letter_correspondence_address = Subscription.objects.get(
            slug="basic-fit-netherlands"
        )
        self.assertFalse(cant_generate_letter.can_generate_pdf())
        self.assertTrue(can_generate_letter_support_address.can_generate_pdf())
        self.assertTrue(can_generate_letter_correspondence_address.can_generate_pdf())

    def test_has_price(self):
        has_no_price = Subscription.objects.get(slug="green-card-lottery")
        has_price = Subscription.objects.get(slug="lottery-usa")
        self.assertFalse(has_no_price.has_registered_price())
        self.assertTrue(has_price.has_registered_price())

    def test_get_address_information(self):
        self.assertEquals(
            Subscription.objects.get(slug="basic-fit-belgie").get_address_information(),
            ("Postbus 12345", "1111AA", "Test city",),
        )
        self.assertEquals(
            Subscription.objects.get(
                slug="basic-fit-netherlands"
            ).get_address_information(),
            ("Test address 1", "2222BB", "Test city",),
        )
        self.assertEquals(
            Subscription.objects.get(
                slug="fit-for-free-belgium"
            ).get_address_information(),
            ("Postbus 12346", "3322AB", "Test city",),
        )

    def test_support_reply_number_prefixed(self):
        self.assertEquals(
            Subscription.objects.get(
                slug="basic-fit-belgie"
            ).support_reply_number_prefixed,
            "Postbus 12345",
        )
        self.assertIsNone(
            Subscription.objects.get(
                slug="basic-fit-netherlands"
            ).support_reply_number_prefixed
        )

    def test_deregistered(self):
        deregistered_subscription_6 = Subscription.objects.get(slug="new-york-times")
        deregistered_subscription_1 = Subscription.objects.get(slug="the-guardian")
        deregistered_subscription_1_created = Subscription.objects.create(
            name="Dutch news", slug="dutch-news",
        )
        deregistered_subscription_6.deregistered()
        deregistered_subscription_1.deregistered()
        deregistered_subscription_1.deregistered()
        deregistered_subscription_1_created.deregistered()
        self.assertEquals(deregistered_subscription_6.amount_used, 7)
        self.assertEquals(deregistered_subscription_1.amount_used, 3)
        self.assertEquals(deregistered_subscription_1_created.amount_used, 2)


class SubscriptionCategoryTest(TestCase):
    fixtures = ["subscriptions.json"]

    def test_get_subcategories(self):
        self.assertQuerysetEqual(
            SubscriptionCategory.objects.get(slug="multimedia").get_subcategories(),
            [
                SubscriptionCategory.objects.get(slug="att"),
                SubscriptionCategory.objects.get(slug="streaming"),
                SubscriptionCategory.objects.get(slug="t-mobile"),
                SubscriptionCategory.objects.get(slug="verizon"),
            ],
        )
        self.assertQuerysetEqual(
            SubscriptionCategory.objects.get(slug="multimedia").get_subcategories(
                order="-name"
            ),
            [
                SubscriptionCategory.objects.get(slug="verizon"),
                SubscriptionCategory.objects.get(slug="t-mobile"),
                SubscriptionCategory.objects.get(slug="streaming"),
                SubscriptionCategory.objects.get(slug="att"),
            ],
        )

    def test_get_top_level_categories(self):
        self.assertCountEqual(
            list(SubscriptionCategory.get_top_level_categories()),
            [
                SubscriptionCategory.objects.get(slug="news-papers"),
                SubscriptionCategory.objects.get(slug="lotteries"),
                SubscriptionCategory.objects.get(slug="fitness"),
                SubscriptionCategory.objects.get(slug="multimedia"),
            ],
        )

    def test_get_family_tree(self):
        self.assertCountEqual(
            SubscriptionCategory.objects.get(slug="multimedia").get_family_tree(),
            [
                SubscriptionCategory.objects.get(slug="multimedia"),
                SubscriptionCategory.objects.get(slug="streaming"),
                SubscriptionCategory.objects.get(slug="netflix"),
                SubscriptionCategory.objects.get(slug="disney-plus"),
                SubscriptionCategory.objects.get(slug="verizon"),
                SubscriptionCategory.objects.get(slug="t-mobile"),
                SubscriptionCategory.objects.get(slug="att"),
            ],
        )

    def test_get_path_to_me(self):
        self.assertEquals(
            SubscriptionCategory.objects.get(slug="netflix").get_path_to_me(),
            [
                SubscriptionCategory.objects.get(slug="multimedia"),
                SubscriptionCategory.objects.get(slug="streaming"),
                SubscriptionCategory.objects.get(slug="netflix"),
            ],
        )
        self.assertEquals(
            SubscriptionCategory.objects.get(slug="basic-fit").get_path_to_me(),
            [
                SubscriptionCategory.objects.get(slug="fitness"),
                SubscriptionCategory.objects.get(slug="basic-fit"),
            ],
        )
