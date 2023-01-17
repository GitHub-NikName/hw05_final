import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import Post, Group


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


def url(url, **kwargs):
    return reverse(url, kwargs=kwargs)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='Группа',
            slug='slug',
            description='Описание'
        )
        cls.post = Post.objects.create(
            text='Пост',
            group=cls.group,
            author=cls.user
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Пост 2',
            'group': self.group.id
        }
        res = self.authorized_client.post(
            url('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            res, url('posts:profile', username=self.user.username)
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        """Текст отредактированного поста изменился"""
        form_data = {
            'text': 'Отредактированный пост',
            'group': self.group.id
        }
        self.authorized_client.post(
            url('posts:post_edit', post_id=self.post.id),
            data=form_data,
            follow=True
        )
        self.assertEqual(
            Post.objects.get(id=self.post.id).text,
            'Отредактированный пост'
        )

    def test_create_post_with_image(self):
        """Валидная форма создает пост с изображением"""
        posts_count = Post.objects.count()
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
            'text': 'Пост 2',
            'group': self.group.id,
            'image': uploaded
        }
        res = self.authorized_client.post(
            url('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            res, url('posts:profile', username=self.user.username)
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
