from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='Группа',
            slug='slug',
            description='Описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Короткий пост',
        )
        cls.long_post = Post.objects.create(
            author=cls.user,
            text='Не более 15 символов может уместиться в превью'
        )

    def test_model_group_object_names_matches_the_title(self):
        """Строковое представление модели Group соответствует названию
         группы"""
        self.assertEqual(str(self.group), 'Группа')

    def test_model_post_object_names_no_more_than_15_characters(self):
        """Строковое представление модели Post не более 15 символов
        текста поста"""
        self.assertEqual(str(self.post), 'Короткий пост')
        self.assertEqual(str(self.long_post), 'Не более 15 сим')
