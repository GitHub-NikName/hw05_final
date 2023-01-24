from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm


def index(request):
    """Главная страница"""
    template = 'posts/index.html'
    post_list = Post.objects.select_related('author', 'group')
    page = get_paginator_page(request, post_list, 10)
    context = {
        'page_obj': page,
        'index': True
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Последние 10 постов в группе"""
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.post_set.all().select_related('author')
    page = get_paginator_page(request, post_list, 10)
    context = {
        'group': group,
        'page_obj': page,
        'title': group.__str__
    }
    return render(request, template, context)


def get_paginator_page(request, post_list, num):
    """Возвращает страницу пагинатора"""
    paginator = Paginator(post_list, num)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return page


def profile(request, username):
    """Страница пользователя"""
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all().select_related('group')
    page = get_paginator_page(request, post_list, 10)
    context = {
        'author': author,
        'page_obj': page
    }
    if request.user.is_authenticated and request.user != author:
        follower = request.user.follower.values_list('author_id', flat=True)
        context['following'] = author.id in follower
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Детальный просмотр публикции"""
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all().select_related('author')
    form = CommentForm()
    context = {
        'post': post,
        'comments': comments,
        'form': form
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Создание новой публикации"""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect(f'/profile/{request.user}/')
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """Редактирование публикации"""
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect(f'/posts/{post_id}/')
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    context = {
        'form': form,
        'is_edit': True
    }
    if form.is_valid():
        form.save()
        return redirect(f'/posts/{post_id}/')
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    follower = request.user.follower.values_list('author_id', flat=True)
    post_list = Post.objects.filter(author__in=follower).\
        select_related('author', 'group')
    page = get_paginator_page(request, post_list, 10)
    context = {
        'page_obj': page,
        'follow': True
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(
            user=request.user,
            author=author
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.get(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)
