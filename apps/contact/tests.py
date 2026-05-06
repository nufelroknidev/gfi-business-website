from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse

from apps.contact.models import Inquiry


class InquiryModelTests(TestCase):

    def test_inquiry_str(self):
        inquiry = Inquiry.objects.create(
            name='John Smith',
            email='john@example.com',
            subject='Product availability',
            message='I would like to know more about your products.',
        )
        self.assertEqual(str(inquiry), 'John Smith — Product availability')

    def test_inquiry_is_unread_by_default(self):
        inquiry = Inquiry.objects.create(
            name='John Smith',
            email='john@example.com',
            subject='Product availability',
            message='I would like to know more about your products.',
        )
        self.assertFalse(inquiry.is_read)


class ContactFormSubmissionTests(TestCase):

    def test_valid_form_saves_to_db(self):
        response = self.client.post(reverse('contact:inquiry'), {
            'name': 'John Smith',
            'email': 'john@example.com',
            'subject': 'Product availability',
            'message': 'I would like to know more about your products.',
        })
        self.assertEqual(Inquiry.objects.count(), 1)

    def test_valid_form_redirects(self):
        response = self.client.post(reverse('contact:inquiry'), {
            'name': 'John Smith',
            'email': 'john@example.com',
            'subject': 'Product availability',
            'message': 'I would like to know more about your products.',
        })
        self.assertEqual(response.status_code, 302)

    def test_invalid_form_does_not_save(self):
        self.client.post(reverse('contact:inquiry'), {
            'name': '',
            'email': 'not-an-email',
            'subject': '',
            'message': '',
        })
        self.assertEqual(Inquiry.objects.count(), 0)

    @override_settings(RATELIMIT_ENABLE=True)
    def test_rate_limit_blocks_after_10_posts(self):
        payload = {
            'name': 'Bot',
            'email': 'bot@example.com',
            'subject': 'Spam',
            'message': 'This is a test message.',
        }
        url = reverse('contact:inquiry')
        for _ in range(10):
            self.client.post(url, payload, REMOTE_ADDR='1.2.3.4')
        response = self.client.post(url, payload, REMOTE_ADDR='1.2.3.4')
        self.assertEqual(response.status_code, 429)

    @patch('apps.contact.views.EmailMessage')
    def test_valid_form_triggers_email(self, mock_email_cls):
        mock_email_cls.return_value.send.return_value = None
        self.client.post(reverse('contact:inquiry'), {
            'name': 'John Smith',
            'email': 'john@example.com',
            'subject': 'Product availability',
            'message': 'I would like to know more about your products.',
        })
        self.assertTrue(mock_email_cls.called)
