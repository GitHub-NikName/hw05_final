from django.test import TestCase
from shortcuts import post, group, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user('user')
        cls.group = group('slug')
        cls.post = post(user=cls.user, text='Короткий пост')
        long_text = 'Не более 15 символов может уместиться в превью'
        cls.long_post = post(user=cls.user, text=long_text)

    def test_model_group_object_names_matches_the_title(self):
        self.assertEqual(str(self.group), 'Группа')

    def test_model_post_object_names_no_more_than_15_characters(self):
        self.assertEqual(str(self.post), 'Короткий пост')
        self.assertEqual(str(self.long_post), 'Не более 15 сим')
