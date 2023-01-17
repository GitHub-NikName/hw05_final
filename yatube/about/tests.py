from django.test import TestCase, Client
from http import HTTPStatus


class AboutTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_url_and_template(self):
        """Страницы и шаблоны приложения about"""
        url_template_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }
        for address, template in url_template_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)
