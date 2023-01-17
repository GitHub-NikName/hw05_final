from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


User = get_user_model()


class PostFormTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_create_user(self):
        form_data = {
            'username': 'user',
            'password1': 'Mkdfnskdvnsdkvndknvdk',
            'password2': 'Mkdfnskdvnsdkvndknvdk'
        }
        res = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(res, reverse('posts:index'))
        self.assertTrue(User.objects.get(username='user'))
