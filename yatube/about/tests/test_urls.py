"""
Модуль предназначен для тестирования статических
страниц сайта.
"""

from django.test import Client, TestCase

STATIC_PAGES = (
    ('/about/author/', 'about/author.html'),
    ('/about/tech/', 'about/tech.html')
)


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_static_urls_adresses(self):
        """
        Тест проверяет, что код ответа на запрос к страницам
        равен 200.
        """

        for page in STATIC_PAGES:
            with self.subTest(page=page):
                response = self.guest_client.get(page[0])
                self.assertEqual(response.status_code, 200)

    def test_static_urls_templates(self):
        """
        Тест проверяет, что страницы используют правильные html
        шаблоны.
        """

        for page in STATIC_PAGES:
            with self.subTest(page=page):
                response = self.guest_client.get(page[0])
                self.assertTemplateUsed(response, page[1])
