from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class PostURLTests(TestCase):
    """Проверка URL адресов."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.urls = [
            reverse('about:author'),
            reverse('about:tech'),
        ]

    def test_url_statik_page_guest_user(self):
        """Проверка дотсупа к страницам не авторизованых пользователей."""
        templates_pages_names = {
            reverse('about:author'),
            reverse('about:tech'),
        }
        for reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(response.status_code, 200)

    def test_about_page_uses_correct_template(self):
        templates_pages_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
