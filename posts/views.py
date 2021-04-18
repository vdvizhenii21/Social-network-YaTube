from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, Follow
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from yatube.settings import PAGINATOR


User = get_user_model()


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, PAGINATOR)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, }
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, PAGINATOR)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'page': page, 'group': group, })


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES)
        if form.is_valid():
            form.instance.author = request.user
            form.save()
            return redirect('index')
        return render(request, 'new.html', {'form': form})
    form = PostForm()
    return render(request, 'new.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user_posts = author.posts.all()
    paginator = Paginator(user_posts, PAGINATOR)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = request.user.is_authenticated and Follow.objects.filter(
        author=author, user=request.user
    ).exists
    context = {
        'page': page,
        'author': author,
        'user_posts': user_posts,
        'following': following,
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    comments = post.comments.all()
    form = CommentForm()
    context = {
        'post': post,
        'author': post.author,
        'comments': comments,
        'form': form,
    }
    return render(request, 'post_view.html', context)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)

    if post.author != request.user:
        return redirect('post', username, post_id)

    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )

    if form.is_valid():
        post.save()
        return redirect('post', username, post_id)

    context = {
        'form': form,
        'post': post,
    }
    return render(request, 'new.html', context)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        form.save()
        return redirect('post', username=username, post_id=post_id)
    else:
        form = CommentForm(request.POST)
    return render(request, 'comments.html', {'form': form, 'post': post})


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, PAGINATOR)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'post_list': post_list}
    return render(request, 'follow.html', context)


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    if request.user == author:
        return redirect('profile', username)
    if not Follow.objects.filter(user=request.user, author=author).exists():
        Follow.objects.create(user=request.user, author=author)
    return redirect('profile', username)


@login_required
def profile_unfollow(request, username):
    unfollow_user = get_object_or_404(User, username=username)
    get_object_or_404(
        Follow,
        user=request.user,
        author=unfollow_user
    ).delete()
    return redirect('profile', username=username)
