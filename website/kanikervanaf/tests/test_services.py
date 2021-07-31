from django.test import TestCase
from django.core import mail
from kanikervanaf.services import send_contact_email


class KanikervanafServices(TestCase):
    def test_send_contact_email(self):
        self.assertEqual(
            send_contact_email("Test name", "test@test.com", "Test title", "content"),
            True,
        )
        self.assertEqual(len(mail.outbox), 1)
