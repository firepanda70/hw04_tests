from django.test import Client, TestCase


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.pages = ('author', 'tech')

    def test_static_urls_adresses(self):
        for page in self.pages:
            with self.subTest(page=page):
                response = self.guest_client.get(f'/about/{page}/')
                self.assertEqual(response.status_code, 200)

    def test_static_urls_templates(self):
        for page in self.pages:
            with self.subTest(page=page):
                response = self.guest_client.get(f'/about/{page}/')
                self.assertTemplateUsed(response, f'about/{page}.html')
