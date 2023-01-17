from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus
from ..models import Post, Group

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Группа',
            slug='slug',
            description='Описание'
        )
        cls.post = Post.objects.create(
            text='Пост',
            author=cls.author,
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_urls_and_templates_exists_all_users(self):
        """Страницы и используемые шаблоны для всех пользователей"""
        url_template_names = {
            '/': 'posts/index.html',
            '/group/slug/': 'posts/group_list.html',
            '/profile/user/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
        }
        for address, template in url_template_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_create_url_and_template_exists_authorized_user(self):
        """Страница создания поста доступна авторизированному пользователю
         и использует шаблон create_post"""
        template = 'posts/create_post.html'
        address = '/create/'
        response = self.authorized_client.get(address)
        guest_res = self.guest_client.get(address, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, template)
        self.assertRedirects(guest_res, f'/auth/login/?next={address}')

    def test_urls_and_templates_exists_author(self):
        """Страница редактирования поста доступна автору поста и использует
         шаблон create_post"""
        template = 'posts/create_post.html'
        address = '/posts/1/edit/'
        response = self.author_client.get(address)
        non_author_res = self.authorized_client.get(address)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, template)
        self.assertRedirects(non_author_res, '/posts/1/')

    def test_url_unexisting_page(self):
        """Несуществующая страница"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
