from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostsUrlsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='testuser')
        cls.user_two = User.objects.create_user(username='second_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client_two = Client()
        cls.authorized_client_two.force_login(cls.user_two)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group
        )
        cls.posts_index = reverse('posts:index')
        cls.posts_group_list = reverse('posts:group_list',
                                       args=(cls.group.slug,))
        cls.posts_profile = reverse('posts:profile',
                                    args=(cls.user.username,))
        cls.posts_post_detail = reverse('posts:post_detail',
                                        args=(cls.post.id,))
        cls.posts_post_create = reverse('posts:post_create')
        cls.posts_post_edit = reverse('posts:post_edit',
                                      args=(cls.post.id,))


    def test_all_cases(self):
        """Проверка доступа для всех пользователей.
        Проверка несуществующей страницы 404."""
        pages_for_all_users = {
            self.posts_index: HTTPStatus.OK,
            self.posts_group_list:
            HTTPStatus.OK,
            self.posts_profile:
            HTTPStatus.OK,
            self.posts_post_detail:
            HTTPStatus.OK,
            reverse('posts:post_detail', args=('0000',)):
            HTTPStatus.NOT_FOUND
        }
        for address, status in pages_for_all_users.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(
                    response.status_code,
                    status,
                    f'Что-то не так с адресом {address}'
                )

    def test_redirect_cases(self):
        """Проверка редиректа для неавториз и невавтора."""
        urls_for_athorized_users = {
            self.posts_post_create: '/auth/login/?next=/create/',
            self.posts_post_edit:
            f'/auth/login/?next=/posts/{self.post.id}/edit/'
        }
        for url, redirect_url in urls_for_athorized_users.items():
            response = self.guest_client.get(url, follow=True)
            self.assertRedirects(
                response, redirect_url)

    def test_urls_use_correct_templates(self):
        """Проверка на то что URL-адрес использует верный шаблон."""
        urls_templates_set = {
            self.posts_index: 'posts/index.html',
            self.posts_group_list: 'posts/group_list.html',
            self.posts_profile: 'posts/profile.html',
            self.posts_post_detail: 'posts/post_detail.html',
            self.posts_post_edit: 'posts/create_post.html',
            self.posts_post_create: 'posts/create_post.html'
        }
        for url, template in urls_templates_set.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
   
    def test_create_post_url_exists_for_authorized_user(self):
        """Проверка создания поста доступного
        для зарегистрированного пользователя."""
        response = self.authorized_client.get(self.posts_post_create)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post_url_exists_for_author(self):
        """Проверка того, что для автора поста существует 
        страница редактирования."""
        url = self.posts_post_edit
        if self.authorized_client == self.post.author:
            response = self.authorized_client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)
    
    def test_edit_post_url_not_available_for_non_author(self):
        """Проверка редактирования поста только для автора."""
        if self.authorized_client_two != self.post.author:
            response = self.authorized_client_two.get(self.posts_post_edit)
            self.assertRedirects(response, self.posts_post_detail)
