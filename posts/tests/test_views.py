from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from yatube.settings import PAGINATOR
from posts.models import Post, Group, Follow
import shutil
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache


User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create_user(username='ScouserVT')
        cls.follower_user = User.objects.create_user(username='Fare')
        cls.group = Group.objects.create(
            title='Test',
            slug='testslug',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.test_user,
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        test_user = PostPagesTests.test_user
        follower_user = PostPagesTests.follower_user
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(test_user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(follower_user)

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'index.html': reverse('index'),
            'new.html': reverse('new_post'),
            'group.html': (
                reverse('group_posts', kwargs={'slug': self.group.slug})
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def post_on_page(self, response):
        if 'post' in response.context:
            first_post = response.context['post']
        else:
            first_post = response.context['page'][0]
        post_text_0 = first_post.text
        post_author_0 = first_post.author
        post_group_0 = first_post.group
        post_image_0 = first_post.image
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, self.post.author)
        self.assertEqual(post_group_0, self.post.group)
        self.assertEqual(post_image_0, self.post.image)

    def test_follow_index_page(self):
        Follow.objects.create(author=self.test_user, user=self.follower_user)
        response = self.authorized_client2.get(reverse('follow_index'))
        self.post_on_page(response)

    def test_home_page_shows_correct_context(self):
        response = self.authorized_client.get(reverse('index'))
        self.post_on_page(response)

    def test_group_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': self.group.slug})
        )
        self.assertEqual(response.context['group'], self.group)

    def test_post_edit_correct_context(self):
        response = self.authorized_client.get(
            reverse('post_edit', args=[self.test_user, self.post.id])
        )
        self.post_on_page(response)

    def test_profile_correct_context(self):
        response = self.authorized_client.get(
            reverse('profile', args=[self.test_user])
        )
        self.post_on_page(response)
        self.assertEqual(response.context['author'], self.test_user)

    def test_post_view_correct_context(self):
        response = self.authorized_client.get(
            reverse('post', args=[self.test_user, self.post.id])
        )
        self.post_on_page(response)

    def test_first_page_containse_ten_records(self):
        objs = [
            Post(
                text=f'Текст тестового поста {i}',
                group=self.group,
                author=self.test_user
            )
            for i in range(1, 13)
        ]
        Post.objects.bulk_create(objs)
        response1 = self.client.get(reverse('index'))
        response2 = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(
            len(response1.context.get('page').object_list), PAGINATOR
        )
        self.assertEqual(len(response2.context.get('page').object_list), 3)

    def test_index_cache_in(self):
        response_before = self.authorized_client.get(reverse('index'))
        self.post = Post.objects.create(
            text='new_text_note',
            author=self.test_user,
            group=self.group
        )
        response_after = self.authorized_client.get(reverse('index'))
        self.assertEqual(
            response_before.content,
            response_after.content
        )

        cache.clear()

        response_after = self.authorized_client.get(reverse('index'))
        self.assertNotEqual(
            response_before.content,
            response_after.content
        )

    def test_follow(self):
        follow_count = Follow.objects.count()
        self.authorized_client2.get(
            reverse('profile_follow', args={self.test_user})
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        last_object = Follow.objects.last()
        self.assertEqual(last_object.author, self.test_user)
        self.assertEqual(last_object.user, self.follower_user)

    def test_unfollow(self):
        follow_count = Follow.objects.count()
        Follow.objects.create(author=self.test_user, user=self.follower_user)
        self.authorized_client2.get(
            reverse('profile_unfollow', args={self.test_user})
        )
        self.assertEqual(Follow.objects.count(), follow_count)
