import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm
from django.views.generic import ListView, DetailView, FormView
from django.views.generic.detail import SingleObjectMixin


class Index(ListView):
    template_name = 'posts/index.html'
    queryset = Post.objects.select_related('author', 'group')
    paginate_by = 10
    extra_context = {'index': True}


class GroupPosts(SingleObjectMixin, Index):
    template_name = 'posts/group_list.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Group.objects.all())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.object
        context['title'] = self.object.__str__
        return context

    def get_queryset(self):
        return self.object.post_set.all().select_related('author')


class FollowIndex(LoginRequiredMixin, Index):
    template_name = 'posts/follow.html'
    extra_context = {'follow': True}

    def get_queryset(self):
        follower = self.request.user.follower.values_list('author_id', flat=True)
        return Post.objects.filter(author__in=follower).\
            select_related('author', 'group')


class Profile(Index):
    template_name = 'posts/profile.html'

    def get(self, request, *args, **kwargs):
        self.author = get_object_or_404(User, username=kwargs['username'])
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = self.author
        if self.request.user.is_authenticated and self.request.user != self.author:
            follower = self.request.user.follower.values_list('author_id', flat=True)
            context['following'] = self.author.id in follower
        return context

    def get_queryset(self):
        return self.author.posts.all().select_related('group')


class PostDetail(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = context['post'].comments.all().select_related('author')
        context['form'] = CommentForm()
        return context


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
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', pk=pk)




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
