from django.urls import reverse
from posts.models import Post, Group, User


_counter = 0


def unique_string(prefix=""):
    global _counter
    _counter += 1
    return prefix + str(_counter)


def url(url, **kwargs):
    return reverse(url, kwargs=kwargs)


def post(user, group=None, text=None, image=None):
    if not text:
        text = unique_string("post")
    if isinstance(user, str):
        user, _ = User.objects.get_or_create(user)
    return Post.objects.create(
        text=text,
        author=user,
        group=group,
        image=image
    )


def group(slug=None, title=None, description=None):
    if not slug:
        slug = unique_string('slug')
    if not description:
        description = 'Описание'
    if not title:
        title = 'Группа'
    return Group.objects.create(
        title=title,
        slug=slug,
        description=description
    )
