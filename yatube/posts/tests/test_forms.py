from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus
from posts.models import Group, Post, User

POST_CREATE_URL = reverse('posts:post_create')
INDEX_URL = reverse('posts:index')
LOGIN_URL = reverse('login')
USERNAME = 'author'
PROFILE_URL = reverse('posts:profile', kwargs={'username': USERNAME})


class PostsFormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test_slug',
            description='Тестовое описание группы',
        )
        cls.group2 = Group.objects.create(
            title='Тестовое название группы-2',
            slug='test_slug2',
            description='Тестовое описание группы-2',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.POST_EDIT_URL = reverse(
            'posts:post_edit',
            kwargs={'post_id': cls.post.id},
        )
        cls.POST_DETAIL_URL = reverse(
            'posts:post_detail',
            kwargs={'post_id': cls.post.id})

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_posts_forms_create_post(self):
        """Проверка, создает ли форма пост в базе."""
        posts_count = Post.objects.count()
        FORM_DATA = {
            'text': 'Тестовый пост',
            'group': self.group.id}
        response = self.authorized_client.post(
            POST_CREATE_URL,
            data=FORM_DATA)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertRedirects(response, PROFILE_URL)
        post = Post.objects.last()
        self.assertEqual(post.text, FORM_DATA['text'])
        self.assertEqual(post.author, self.author)
        self.assertEqual(post.group_id, FORM_DATA['group'])

    def test_authorized_user_edit_post(self):
        """Проверка редактирования записи авторизированным клиентом."""
        form_data = {
            'text': 'Отредактированный текст поста',
            'group': self.group2.id,
        }
        response = self.authorized_client.post(
            self.POST_EDIT_URL,
            data=form_data,
        )
        self.assertRedirects(
            response,
            self.POST_DETAIL_URL
        )
        old_group_response = self.authorized_client.get(
            reverse('posts:group_list', args=(self.group.slug,))
        )
        post = Post.objects.get(pk=self.post.pk)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group_id, form_data['group'])
        self.assertEqual(
            old_group_response.context['page_obj'].paginator.count, 0
        )

    def test_nonauthorized_user_create_post(self):
        """Проверка создания записи не авторизированным пользователем."""
        FORM_DATA = {
            'text': 'Тестовый пост',
            'group': self.group.id}
        posts_before = set(Post.objects.all())
        response = self.guest_client.post(
            POST_CREATE_URL,
            data=FORM_DATA)
        posts_after = set(Post.objects.all())
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        redirect = LOGIN_URL + '?next=' + POST_CREATE_URL
        self.assertRedirects(response, redirect)
        self.assertEqual(posts_before, posts_after)
