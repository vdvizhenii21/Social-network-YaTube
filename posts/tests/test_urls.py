# posts/tests/tests_url.py
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from posts.models import Post, Group
from django.urls import reverse

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create_user(username='ScouserVT')
        cls.group = Group.objects.create(
            title='Test',
            slug='testslug',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.test_user,
            group=cls.group,
        )

    def setUp(self):
        test_user = PostURLTests.test_user
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(test_user)

    def test_error_page(self):
        response = self.guest_client.get('in/1')
        self.assertEqual(response.status_code, 404)

    # Общедоступные страницы
    def test_homepage(self):
        response = self.guest_client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_group_slug(self):
        response = self.guest_client.get(
            reverse('group_posts', args=[self.group.slug])
        )
        self.assertEqual(response.status_code, 200)

    def test_profile(self):
        response = self.guest_client.get(reverse(
            'profile', args=[self.test_user]
        ))
        self.assertEqual(response.status_code, 200)

    def test_post_view(self):
        response = self.guest_client.get(reverse(
            'post', args=[self.test_user, self.post.id]
        ))
        self.assertEqual(response.status_code, 200)

    def test_post_edit_guest(self):
        response = self.guest_client.get(reverse(
            'post_edit', args=[self.test_user, self.post.id]
        ))
        self.assertEqual(response.status_code, 302)

    # Для авторизированых
    def test_post_edit(self):
        response = self.authorized_client.get(reverse(
            'post_edit', args=[self.test_user, self.post.id]
        ))
        self.assertEqual(response.status_code, 200)

    def test_create_new_post(self):
        response = self.authorized_client.get(reverse('new_post'))
        self.assertEqual(response.status_code, 200)

    def test_guest_new_accesses(self):
        """Проверяем редирект гостя с создания новой записи на авторизацию"""
        page_access = self.guest_client.get(reverse('new_post'))
        self.assertRedirects(
            page_access, reverse('login') + '?next=' + reverse('new_post')
        )

    # Проверка вызываемых шаблонов для каждого адреса
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'index.html': reverse('index'),
            'new.html': reverse('new_post'),
            'group.html': (
                reverse('group_posts', kwargs={'slug': self.group.slug})
            ),
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_url_post_edit_correct_template(self):
        response = self.authorized_client.get(reverse(
            'post_edit', args=[self.test_user, self.post.id]
        ))
        self.assertTemplateUsed(response, 'new.html')

    def test_guest_new_edit_accesses(self):
        follower_user = User.objects.create_user(username='Fare')
        authorized_client2 = Client()
        authorized_client2.force_login(follower_user)
        response = authorized_client2.get(reverse(
            'post_edit', args=[self.test_user, self.post.id]
        ))
        self.assertRedirects(
            response, reverse(
                'post', args=[self.test_user, self.post.id]
            ))
