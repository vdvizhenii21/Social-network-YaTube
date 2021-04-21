import shutil
import tempfile
from django.test.utils import override_settings
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.test import Client, TestCase
from posts.models import Post, Group, User, Comment
from django.urls import reverse


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(dir=settings.BASE_DIR))
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='ScouserVT')
        cls.group = Group.objects.create(
            title='Test',
            slug='testslug',
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.group = PostCreateFormTests.group
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        post_count = Post.objects.count()
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
        form_data = {
            'group': self.group.id,
            'text': 'Тестовый текст',
            'image': uploaded,
        }

        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )

        post_last = Post.objects.last()
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(post_last.text, form_data['text'])
        self.assertEqual(post_last.group, self.group)
        self.assertEqual(post_last.author, self.user)
        self.assertIsNotNone(post_last.image)

    def test_post_edit(self):
        self.post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group,
        )
        post_count = Post.objects.count()

        form_data = {
            'group': self.group.id,
            'text': 'мир',
        }

        response = self.authorized_client.post(
            reverse('post_edit', args=[self.user, self.post.id]),
            data=form_data,
            follow=True
        )

        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(Post.objects.last().text, form_data['text'])
        self.assertRedirects(response, reverse(
            'post', args=[self.user, self.post.id]
        ))

    def test_post_edit_uknown_user(self):
        post_count = Post.objects.count()
        response = self.guest_client.get(reverse(
            'new_post'))
        self.assertEqual(Post.objects.count(), post_count)
        self.assertRedirects(
            response, reverse('login') + '?next=' + reverse('new_post')
        )

    def test_add_comment(self):
        post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group,
        )
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый текст',

        }
        response = self.authorized_client.post(
            reverse('add_comment', args=[self.user, post.id]),
            data=form_data,
            follow=True
        )
        comment_last = Comment.objects.last()
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertEqual(comment_last.text, form_data['text'])
        self.assertRedirects(response, reverse(
            'post', args=[self.user, post.id]
        ))
        self.assertEqual(comment_last.author, self.user)
        self.assertEqual(comment_last.post.id, post.id)

    def test_post_edit_uknown_user(self):
        self.post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group,
        )
        comment_count = Comment.objects.count()
        self.guest_client.post(
            reverse('add_comment', args=[self.user, self.post.id])
        )
        self.assertEqual(Comment.objects.count(), comment_count)
