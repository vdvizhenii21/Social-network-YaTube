from django.contrib.auth import get_user_model
from django.forms import ModelForm, Textarea
from .models import Comment

from .models import Post

User = get_user_model()


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ["text", "group", "image"]
        labels = {
            "text": "Напишите о чем Ваш пост: ",
            "group": "Выберите группу: ",
        }

        widgets = {
            "text": Textarea(attrs={
                "class": "form-contol",
                "placeholder": "Новый пост"
            })
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
