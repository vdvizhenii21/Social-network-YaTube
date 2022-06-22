from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        "Заголовок",
        max_length=200,
        help_text="Дайте подробное описание группе"
    )
    slug = models.SlugField(
        "Слаг",
        max_length=100,
        unique=True,
        blank=True,
        help_text=("Укажите адрес для страницы группы. Используйте только "
                   "латиницу, цифры, дефисы и знаки подчёркивания"),
    )
    description = models.TextField(
        "Текст",
        help_text="Опишите суть группы",
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        "Текст",
        help_text="Дайте короткое описание поста"
    )
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts")
    group = models.ForeignKey(
        Group,
        verbose_name="Choose a group",
        help_text="Select a group from existing",
        on_delete=models.SET_NULL,
        related_name="posts",
        blank=True,
        null=True)
    image = models.ImageField(upload_to="posts/", blank=True, null=True)

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        related_name="comments",
        on_delete=models.CASCADE,
        blank=True,
        null=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments")
    text = models.TextField(
        "Комментарий",
        help_text="Напишите комментарий"
    )
    created = models.DateTimeField("date created", auto_now_add=True)

    class Meta:
        ordering = ["created"]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following")
