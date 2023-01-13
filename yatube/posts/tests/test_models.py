# from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.assertEqual(self.post.text[:15], str(self.post))
        self.assertEqual(self.group.title, str(self.group))

    def test_post_model_verbose(self):
        """Проверяем поле verbose."""
        post = self.post
        fields = {
            post._meta.get_field('text').verbose_name: 'Текст поста',
            post._meta.get_field('author').verbose_name: 'Автор',
            post._meta.get_field('group').verbose_name: 'Группа',
            post._meta.get_field('text').help_text: 'Введите текст поста'
        }
        for field, text in fields.items():
            with self.subTest():
                self.assertEqual(field, text)

    def test_post_model_help_text(self):
        """Проверяем поле help_text."""
        post = self.post
        fields = {
            post._meta.get_field('text').help_text: 'Введите текст поста',
            post._meta.get_field('group').help_text: 'Выберите группу',
        }
        for field, text in fields.items():
            with self.subTest():
                self.assertEqual(field, text)
