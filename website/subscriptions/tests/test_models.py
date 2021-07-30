from django.test import TestCase

from subscriptions.models import (
    Subscription,
    SubscriptionObject,
    SubscriptionCategory,
    SubscriptionSearchTerm,
    TEMPLATE_FILE_DIRECTORY,
)
from django.core.files import File
from django.conf import settings
import os
import shutil

from mock import MagicMock


class SubscriptionObjectTest(TestCase):
    fixtures = ["subscriptions.json"]

    @staticmethod
    def _get_template_name(subscription_object, template_name):
        return os.path.join(
            settings.MEDIA_ROOT,
            TEMPLATE_FILE_DIRECTORY
            + "{}/{}/{}".format(
                subscription_object._meta.model_name,
                subscription_object.slug,
                template_name,
            ),
        )

    @staticmethod
    def _remove_template_files(subscription_object: SubscriptionObject):
        shutil.rmtree(
            os.path.join(
                settings.MEDIA_ROOT,
                TEMPLATE_FILE_DIRECTORY
                + "{}/{}".format(
                    subscription_object._meta.model_name, subscription_object.slug,
                ),
            ),
            ignore_errors=True,
        )

    @classmethod
    def setUpTestData(cls):
        cls.subscription_mocked_letter_template = Subscription.objects.get(
            slug="t-mobile-data"
        )
        cls.subscription_mocked_email_template = Subscription.objects.get(
            slug="basic-fit-netherlands"
        )
        cls.subscription_category_mocked_templates = SubscriptionCategory.objects.get(
            slug="multimedia"
        )
        cls.subscription_mocked_letter_template_for_category = Subscription.objects.get(
            slug="t-mobile-phone"
        )
        cls.subscription_no_mocked_email_template = Subscription.objects.get(
            slug="green-card-lottery"
        )

        # Remove items in the upload folders (in case they exist)
        cls._remove_template_files(cls.subscription_mocked_letter_template)
        cls._remove_template_files(cls.subscription_mocked_email_template)
        cls._remove_template_files(cls.subscription_category_mocked_templates)

        # Upload files to the respective objects
        cls.mocked_letter_template = MagicMock(spec=File)
        cls.mocked_letter_template.name = "this-is-a-random-name.html"
        cls.mocked_email_template = MagicMock(spec=File)
        cls.mocked_email_template.name = "this-is-a-random-name.txt"
        cls.subscription_mocked_letter_template.letter_template.save(
            cls.mocked_letter_template.name, cls.mocked_letter_template
        )
        cls.subscription_mocked_email_template.email_template_text.save(
            cls.mocked_email_template.name, cls.mocked_email_template
        )
        cls.subscription_category_mocked_templates.letter_template.save(
            cls.mocked_letter_template.name, cls.mocked_letter_template
        )
        cls.subscription_category_mocked_templates.email_template_text.save(
            cls.mocked_email_template.name, cls.mocked_email_template
        )

    def tearDown(self):
        self._remove_template_files(self.subscription_mocked_letter_template)
        self._remove_template_files(self.subscription_mocked_email_template)
        self._remove_template_files(self.subscription_category_mocked_templates)

    def test_letter_template_full_path(self):
        self.assertEqual(
            self.subscription_mocked_letter_template.letter_template_full_path,
            self._get_template_name(
                self.subscription_mocked_letter_template, "letter_template.html"
            ),
        )

    def test_email_template_full_path(self):
        self.assertEqual(
            self.subscription_mocked_email_template.email_template_text_full_path,
            self._get_template_name(
                self.subscription_mocked_email_template, "email_template.txt"
            ),
        )

    def test_get_letter_template(self):
        self.assertEqual(
            self.subscription_mocked_letter_template.get_letter_template(),
            self._get_template_name(
                self.subscription_mocked_letter_template, "letter_template.html"
            ),
        )
        self.assertEqual(
            self.subscription_mocked_letter_template_for_category.get_letter_template(),
            self._get_template_name(
                self.subscription_category_mocked_templates, "letter_template.html"
            ),
        )
        self.assertEqual(
            self.subscription_mocked_email_template.get_letter_template(),
            os.path.join(
                settings.BASE_DIR, "subscriptions/templates/pdf/deregister_letter.html",
            ),
        )

    def test_get_email_template_text(self):
        self.assertEqual(
            self.subscription_mocked_email_template.get_email_template_text(),
            self._get_template_name(
                self.subscription_mocked_email_template, "email_template.txt"
            ),
        )
        self.assertEqual(
            self.subscription_mocked_letter_template.get_email_template_text(),
            self._get_template_name(
                self.subscription_category_mocked_templates, "email_template.txt"
            ),
        )
        self.assertEqual(
            self.subscription_no_mocked_email_template.get_email_template_text(),
            os.path.join(
                settings.BASE_DIR, "subscriptions/templates/email/deregister_mail.txt",
            ),
        )


class SubscriptionTest(TestCase):
    fixtures = ["subscriptions.json"]

    def test_can_generate_email(self):
        subscription_can_generate_email = Subscription.objects.create(
            name="can-generate-email",
            slug="can-generate-email",
            support_email="something@something.com",
        )
        subscription_cant_generate_email = Subscription.objects.create(
            name="cant-generate-email", slug="cant-generate-email"
        )
        self.assertFalse(subscription_cant_generate_email.can_generate_email)
        self.assertTrue(subscription_can_generate_email.can_generate_email)

    def test_can_generate_letter(self):
        subscription_cant_generate_letter = Subscription.objects.create(
            name="cant-generate-letter", slug="cant-generate-letter"
        )
        subscription_can_generate_letter_support_address = Subscription.objects.create(
            name="can-generate-letter-support-address",
            slug="can-generate-letter-support-address",
            support_reply_number="12345",
            support_postal_code="1111AA",
        )
        subscription_can_generate_letter_correspondence_address = Subscription.objects.create(
            name="can-generate-letter-correspondence-address",
            slug="can-generate-letter-correspondence-address",
            correspondence_address="Test address 1",
            correspondence_postal_code="2222BB",
        )
        self.assertFalse(subscription_cant_generate_letter.can_generate_letter)
        self.assertTrue(
            subscription_can_generate_letter_support_address.can_generate_letter
        )
        self.assertTrue(
            subscription_can_generate_letter_correspondence_address.can_generate_letter
        )

    def test_has_price(self):
        has_no_price = Subscription.objects.get(slug="green-card-lottery")
        has_price = Subscription.objects.get(slug="lottery-usa")
        self.assertFalse(has_no_price.has_registered_price())
        self.assertTrue(has_price.has_registered_price())

    def test_get_address_information(self):
        self.assertEqual(
            Subscription.objects.get(slug="basic-fit-belgie").get_address_information(),
            ("Postbus 12345", "1111AA", "Test city",),
        )
        self.assertEqual(
            Subscription.objects.get(
                slug="basic-fit-netherlands"
            ).get_address_information(),
            ("Test address 1", "2222BB", "Test city",),
        )
        self.assertEqual(
            Subscription.objects.get(
                slug="fit-for-free-belgium"
            ).get_address_information(),
            ("Postbus 12346", "3322AB", "Test city",),
        )

    def test_support_reply_number_prefixed(self):
        self.assertEqual(
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
        self.assertEqual(deregistered_subscription_6.amount_used, 7)
        self.assertEqual(deregistered_subscription_1.amount_used, 3)
        self.assertEqual(deregistered_subscription_1_created.amount_used, 2)


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
        self.assertEqual(
            SubscriptionCategory.objects.get(slug="netflix").get_path_to_me(),
            [
                SubscriptionCategory.objects.get(slug="multimedia"),
                SubscriptionCategory.objects.get(slug="streaming"),
                SubscriptionCategory.objects.get(slug="netflix"),
            ],
        )
        self.assertEqual(
            SubscriptionCategory.objects.get(slug="basic-fit").get_path_to_me(),
            [
                SubscriptionCategory.objects.get(slug="fitness"),
                SubscriptionCategory.objects.get(slug="basic-fit"),
            ],
        )
