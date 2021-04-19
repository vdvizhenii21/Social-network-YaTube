from posts.models import Post, Group, User

from django.test import TestCase


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            text='Тестовый текст, должен быть не меньше 15 символов!',
            author=User.objects.create_user(username='TestName'),
        )
        cls.group = Group.objects.create(
            title='Test',
            slug='test-task',
            description='тестовое описание'
        )

    def test_text_post_label(self):
        post = PostModelTest.post
        verbose = post._meta.get_field('text').verbose_name
        self.assertEquals(verbose, 'Текст')

    def test_verbose_name(self):
        group = PostModelTest.group
        field_verboses = {
            'title': 'Заголовок',
            'slug': 'Слаг',
            'description': 'Текст',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        group = PostModelTest.group
        field_help_texts = {
            'title': 'Дайте подробное описание группе',
            'slug': ('Укажите адрес для страницы группы. Используйте '
                     'только латиницу, цифры, дефисы и знаки '
                     'подчёркивания'),
            'description': 'Опишите суть группы'
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_post_text_str(self):
        post = PostModelTest.post
        text = post.text
        self.assertEqual(str(post), text[:15])

    def test_group_str(self):
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
