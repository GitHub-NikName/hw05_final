import tempfile
import shutil

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.conf import settings

from ..models import Post, Follow
from ..forms import PostForm

from shortcuts import url, post, group


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user('user')
        cls.group = group('slug')
        [post(cls.user, cls.group) for _ in range(12)]
        # post(cls.user, batch_size=12)
        cls.urls = [
            url('posts:index'),
            url('posts:group_list', slug=cls.group.slug),
            url('posts:profile', username=cls.user.username),
            url('posts:post_detail', post_id=1),
            url('posts:post_edit', post_id=1),
            url('posts:post_create'),
        ]
        cls.templates = [
            'posts/index.html',
            'posts/group_list.html',
            'posts/profile.html',
            'posts/post_detail.html',
            'posts/create_post.html',
            'posts/create_post.html',
        ]
        image_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.image = SimpleUploadedFile(
            name='image.gif',
            content=image_gif,
            content_type='image/gif'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.post_img = post('user', group=self.group, image=self.image)
        self.client = Client()
        self.client.force_login(self.user)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for address, template in zip(self.urls, self.templates):
            with self.subTest(address):
                res = self.client.get(address)
                self.assertTemplateUsed(res, template)

    def test_index_url_contains_list_of_posts(self):
        res = self.client.get(url('posts:index'))
        post_list = list(res.context.get('page_obj'))
        self.assertIsInstance(post_list, list)
        self.assertIsInstance(post_list[0], Post)

    def test_group_list_url_contains_list_of_posts_filtered_by_group(self):
        res = self.client.get(url('posts:group_list', slug=self.group.slug))
        post_list = res.context.get('page_obj').object_list
        self.assertIsInstance(post_list, list)
        self.assertIsInstance(post_list[0], Post)
        self.assertTrue(all(post.group == self.group for post in post_list))

    def test_profile_url_contains_list_of_posts_filtered_by_user(self):
        res = self.client.get(url('posts:profile', username='user'))
        post_list = res.context.get('page_obj').object_list
        self.assertIsInstance(post_list, list)
        self.assertIsInstance(post_list[0], Post)
        self.assertTrue(all(post.author == self.user for post in post_list))

    def test_post_detail_url_contains_post_filtered_by_id(self):
        res = self.client.get(url('posts:post_detail', post_id=1))
        post = res.context.get('post')
        self.assertIsInstance(post, Post)
        self.assertEqual(post.id, 1)

    def test_post_edit_url_contains_form_with_post_filtered_by_id(self):
        res = self.client.get(url('posts:post_edit', post_id=1))
        form = res.context.get('form')
        self.assertIsInstance(form, PostForm)
        self.assertEqual(form.instance.id, 1)
        self.assertEqual(form.instance.text, Post.objects.get(id=1).text)

    def test_create_post_url_contains_form(self):
        res = self.client.get(url('posts:post_create'))
        form = res.context.get('form')
        self.assertIsInstance(form, PostForm)
        self.assertEqual(form.instance.text, '')

    def test_paginator_pages_contains_10_and_3_posts(self):
        for address in self.urls:
            res = self.client.get(address)
            if res.context.get('page_obj'):
                self.assertEqual(len(res.context['page_obj']), 10)
                res = self.client.get(address + '?page=2')
                self.assertEqual(len(res.context['page_obj']), 3)

    def test_post_with_group_added_on_index_post_list_and_profile_pages(self):
        """Пост с указанной группой отображается на страницах: главной, группы,
         пользователя"""
        expected = Post.objects.first()
        for address in self.urls:
            res = self.client.get(address)
            if res.context.get('page_obj'):
                post = res.context.get('page_obj').object_list[0]
                self.assertEqual(post, expected)

    def test_post_list_url_contains_added_post(self):
        """Созданный пост в своей группе."""
        res = self.client.get(url('posts:group_list', slug=self.group.slug))
        expected = Post.objects.exclude(group=self.group)
        posts = res.context["page_obj"]
        self.assertNotIn(posts, expected)

    def test_post_with_image_on_index_post_list_profile_pages(self):
        urls = [
            url('posts:index'),
            url('posts:group_list', slug=self.group.slug),
            url('posts:profile', username=self.user.username),
        ]
        for address in urls:
            with self.subTest(address):
                res = self.client.get(address)
                self.assertTrue(res.context.get('page_obj')[0].image)

    def test_post_with_image_on_detail_pages(self):
        res = self.client.get(url('posts:post_detail', post_id=13))
        self.assertTrue(res.context.get('post').image)


class PostCommentsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user('user')

    def setUp(self):
        self.post = post(self.user)
        self.guest_client = Client()
        self.client = Client()
        self.client.force_login(self.user)
        cache.clear()

    def test_post_detail_url_for_authorized_user_contains_comment_form(self):
        res = self.client.get(url('posts:post_detail', post_id=self.post.id))
        self.assertTrue(res.context.get('form'))

    def test_only_authorized_user_can_comment_on_posts(self):
        """Комментировать посты может только авторизованный пользователь"""
        form_data = {'text': 'Комментарий'}
        comments = self.post.comments.count()
        self.client.post(
            url('posts:add_comment', post_id=self.post.id),
            data=form_data,
            follow=True
        )
        self.assertEqual(self.post.comments.count(), comments + 1)
        self.guest_client.post(
            url('posts:add_comment', post_id=self.post.id),
            data=form_data,
            follow=True
        )
        self.assertEqual(self.post.comments.count(), comments + 1)

    def test_after_submitting_comment_on_the_post_page(self):
        """После успешной отправки комментарий появляется на странице поста"""
        count = self.post.comments.count()
        form_data = {'text': 'Комментарий'}
        self.client.post(
            url('posts:add_comment', post_id=self.post.id),
            data=form_data,
            follow=True
        )
        res = self.client.get(url('posts:post_detail', post_id=self.post.id))
        self.assertEqual(self.post.comments.count(), count + 1)
        self.assertTrue(res.context.get('comments').first())


class PostFollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user('author')
        cls.user = User.objects.create_user('user')

    def setUp(self):
        self.post = post(self.author)
        self.client = Client()
        self.client.force_login(self.author)
        self.user_client = Client()
        self.user_client.force_login(self.user)
        cache.clear()

    def test_profile_follow_and_profile_unfollow_for_authorized_user(self):
        """Авторизованный пользователь может подписываться на других
         пользователей и удалять их из подписок"""
        followers = self.user.follower.all().count()
        self.user_client.get(url('posts:profile_follow', username='author'))
        self.assertEqual(self.user.follower.all().count(), followers + 1)
        self.user_client.get(url('posts:profile_unfollow', username='author'))
        self.assertEqual(self.user.follower.all().count(), followers)

    def test_new_post_in_follow_page(self):
        """Новая запись пользователя появляется в ленте тех, кто на него
         подписан и не появляется в ленте тех, кто не подписан."""
        res = self.user_client.get(url('posts:follow_index'))
        self.assertEqual(len(res.context.get('page_obj')), 0)
        Follow.objects.create(user=self.user, author=self.author)
        res_2 = self.user_client.get(url('posts:follow_index'))
        self.assertEqual(len(res_2.context["page_obj"]), 1)
        #  не подписчик
        res_3 = self.client.get(url('posts:follow_index'))
        self.assertEqual(len(res_3.context["page_obj"]), 0)


class PostCashTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user('user')

    def setUp(self):
        self.post = post(self.user)
        self.client = Client()
        self.client.force_login(self.user)
        cache.clear()

    def test_index_cache(self):
        """Главная страница кеширована на 20 секунд"""
        content_1 = self.client.get(url('posts:index')).content
        Post.objects.get(id=self.post.id).delete()
        content_2 = self.client.get(url('posts:index')).content
        self.assertEqual(content_1, content_2)
        cache.clear()
        content_3 = self.client.get(url('posts:index')).content
        self.assertNotEqual(content_2, content_3)


# class TestTmp(TestCase):
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         cls.user = User.objects.create_user('user')
#         post('user', 12)
#
#     def setUp(self):
#         self.client = Client()
#         self.client.force_login(self.user)
#
#     def test_count(self):
#         self.assertEqual(Post.objects.count(), 12)
