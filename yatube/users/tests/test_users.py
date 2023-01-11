import secrets

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


User = get_user_model()


class UserCreateTests(TestCase):

    def setUp(self):
        self.user_client = Client()

    def test_create_user(self):
        """Проверка что пользователь создается"""
        users_count = User.objects.count()
        password = secrets.token_urlsafe()
        form_data = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'username': 'emplyooo',
            'email': 'emplyooo@gmail.com',
            'password1': password,
            'password2': password,
        }
        response = self.user_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertEqual(response.status_code, 200)
