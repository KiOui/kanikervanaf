from django.test import TestCase
from django.template.exceptions import TemplateSyntaxError
from subscriptions.services import (
    render_string,
    handle_verification_request,
    store_subscription_list,
    render_string_to_pdf,
    render_deregister_letter_pdf,
    send_verification_email,
    send_summary_email,
    create_deregister_letters,
    get_file_contents,
)
from subscriptions.models import Subscription, QueuedMailList
from PyPDF2 import PdfFileReader
from io import BytesIO
from freezegun import freeze_time
import datetime
import tempfile
from django.core import mail


class SubscriptionServices(TestCase):
    fixtures = ["subscriptions.json"]

    def test_render_string(self):
        without_django_engine = (
            "This is a line of text, you can insert your name here: {{ name }}."
        )
        with_django_engine = (
            "{% load static %}By loading static we test whether we are rendering with or without "
            "the Django engine. "
        )
        self.assertEqual(
            render_string(without_django_engine, {"name": "Test name"}),
            "This is a line of text, you can insert your name here: Test name.",
        )
        self.assertEqual(
            render_string(with_django_engine, {}, use_django_engine=True),
            "By loading static we test whether we are rendering with or without the Django engine.",
        )
        with self.assertRaisesMessage(
            TemplateSyntaxError,
            "'static' is not a registered tag library. Must be one of:",
        ):
            render_string(with_django_engine, {"name": "Test name"})

    def test_render_string_to_pdf(self):
        template = "This is a line of text, you can insert your name here: {{ name }}."
        rendered_template = render_string(template, {"name": "Test name"})
        rendered_pdf_as_bytesio = BytesIO(
            render_string_to_pdf(template, {"name": "Test name"})
        )
        pdf_reader = PdfFileReader(rendered_pdf_as_bytesio)
        self.assertEqual(len(pdf_reader.pages), 1)
        page_one = pdf_reader.pages[0]
        extracted_text = page_one.extract_text().replace("\n", "").replace(" ", "")
        self.assertEqual(rendered_template.replace(" ", ""), extracted_text)

    @freeze_time("2020-01-01")
    def test_render_deregister_letter_pdf(self):
        test_subscription = Subscription.objects.get(slug="basic-fit-belgie")
        template = (
            "{{ subscription_address }} {{ subscription_postal_code }} {{ subscription_residence }} {{ "
            "subscription_name }} {{ date }} {{ name }} "
        )
        (
            item_address,
            item_postal_code,
            item_residence,
        ) = test_subscription.get_address_information()
        rendered_template = render_string(
            template,
            {
                "name": "Test name",
                "subscription_address": item_address,
                "subscription_postal_code": item_postal_code,
                "subscription_residence": item_residence,
                "subscription_name": test_subscription.name,
                "date": datetime.datetime.now().strftime("%d-%m-%Y"),
            },
        )

        temporary_template_file = tempfile.NamedTemporaryFile(mode="w")
        temporary_template_file.write(template)
        temporary_template_file.seek(0)

        rendered_pdf_as_bytesio = BytesIO(
            render_deregister_letter_pdf(
                {"name": "Test name"},
                test_subscription,
                letter_template=temporary_template_file.name,
            )
        )
        temporary_template_file.close()
        pdf_reader = PdfFileReader(rendered_pdf_as_bytesio)
        self.assertEqual(len(pdf_reader.pages), 1)
        page_one = pdf_reader.pages[0]
        extracted_text = page_one.extract_text().replace("\n", "").replace(" ", "")
        self.assertEqual(rendered_template.replace(" ", ""), extracted_text)

    def test_send_verification_email(self):
        test_name, test_email, test_verification_url = (
            "Test",
            "test@test.com",
            "https://test.url/verification?code=12345",
        )
        self.assertTrue(
            send_verification_email(test_name, test_email, test_verification_url)
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertCountEqual(mail.outbox[0].to, ["test@test.com"])

    def test_send_summary_email(self):
        succeeded_mails, failed_mails, succeeded_letters, failed_letters, pdfs = (
            {Subscription.objects.get(slug="basic-fit-belgie")},
            set([]),
            {
                Subscription.objects.get(slug="basic-fit-belgie"),
                Subscription.objects.get(slug="new-york-times"),
            },
            {Subscription.objects.get(slug="lottery-usa")},
            [
                {
                    "item": Subscription.objects.get(slug="basic-fit-belgie"),
                    "pdf": render_string_to_pdf("This is a pdf", {}),
                },
                {
                    "item": Subscription.objects.get(slug="new-york-times"),
                    "pdf": render_string_to_pdf("This is another pdf", {}),
                },
            ],
        )
        queued_mail_list = QueuedMailList.generate(
            "Test",
            "Name",
            "test@test.com",
            "Test address 1",
            "1111AA",
            "Test city",
            [
                Subscription.objects.get(slug="basic-fit-belgie"),
                Subscription.objects.get(slug="new-york-times"),
                Subscription.objects.get(slug="lottery-usa"),
            ],
        )
        self.assertTrue(
            send_summary_email(
                succeeded_mails,
                failed_mails,
                succeeded_letters,
                failed_letters,
                pdfs,
                queued_mail_list,
            )
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertCountEqual(mail.outbox[0].to, ["test@test.com"])
        self.assertEqual(len(mail.outbox[0].attachments), 2)

    def test_create_deregister_letters(self):
        queued_mail_list = QueuedMailList.generate(
            "Test",
            "Name",
            "test@test.com",
            "Test address 1",
            "1111AA",
            "Test city",
            [
                Subscription.objects.get(slug="basic-fit-belgie"),
                Subscription.objects.get(slug="basic-fit-netherlands"),
                Subscription.objects.get(slug="new-york-times"),
                Subscription.objects.get(slug="lottery-usa"),
            ],
        )
        succeeded, failed, pdfs = create_deregister_letters(queued_mail_list)
        self.assertCountEqual(
            succeeded,
            [
                Subscription.objects.get(slug="basic-fit-belgie"),
                Subscription.objects.get(slug="basic-fit-netherlands"),
            ],
        )
        self.assertCountEqual(
            failed,
            [
                Subscription.objects.get(slug="new-york-times"),
                Subscription.objects.get(slug="lottery-usa"),
            ],
        )
        self.assertEqual(len(pdfs), 2)

    def test_handle_verification_request(self):
        test_deregister_subscriptions = [
            {"id": x}
            for x in [
                Subscription.objects.get(slug="t-mobile-data").id,
                Subscription.objects.get(slug="fit-for-free-france").id,
                Subscription.objects.get(slug="the-guardian").id,
            ]
        ]
        self.assertIsInstance(
            handle_verification_request(
                {
                    "first_name": "First name test",
                    "second_name": "Second name test",
                    "email": "test@test.com",
                    "address": "Test address",
                    "postal_code": "1111AA",
                    "residence": "Test city",
                },
                test_deregister_subscriptions,
            ),
            QueuedMailList,
        )
        self.assertFalse(
            handle_verification_request(
                {
                    "second_name": "Second name test",
                    "email": "test@test.com",
                    "address": "Test address",
                    "postal_code": "1111AA",
                    "residence": "Test city",
                },
                test_deregister_subscriptions,
            )
        )
        self.assertFalse(
            handle_verification_request(
                {
                    "first_name": "First name test",
                    "second_name": "Second name test",
                    "address": "Test address",
                    "postal_code": "1111AA",
                    "residence": "Test city",
                },
                test_deregister_subscriptions,
            )
        )

    def test_store_subscription_list(self):
        test_subscription_list = [
            Subscription.objects.get(slug="t-mobile-data"),
            Subscription.objects.get(slug="fit-for-free-france"),
            Subscription.objects.get(slug="the-guardian"),
        ]
        test_subscription_items_list = [{"id": x.id} for x in test_subscription_list]
        self.assertCountEqual(
            store_subscription_list(test_subscription_items_list),
            set(test_subscription_list),
        )

    def test_get_file_contents(self):
        test_content = "This is test content for a file."
        temporary_file = tempfile.NamedTemporaryFile(mode="w")
        temporary_file.write(test_content)
        temporary_file.seek(0)

        read_content = get_file_contents(temporary_file.name)
        self.assertEqual(test_content, read_content)
