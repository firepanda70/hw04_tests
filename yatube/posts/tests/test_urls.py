from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='amogus')
        cls.group = Group.objects.create(
            title='Заголовок',
            description='Описание',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Текст'
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)

    def test_urls_access_from_anonimous_user(self):
        urls = (
            '/',
            f'/group/{PostURLTests.group.slug}/',
            f'/{PostURLTests.user.username}/',
            f'/{PostURLTests.user.username}/{PostURLTests.post.pk}/'
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200,
                                 f'fail at getting to "{url}" page')

    def test_urls_access_from_authorised_user(self):
        urls = (
            '/new/',
            f'/{PostURLTests.user.username}/{PostURLTests.post.pk}/edit/'
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, 200,
                                 f'fail at getting to "{url}" page')

    def test_redirect_for_anonimous_user(self):
        urls = (
            '/new/',
            f'/{PostURLTests.user.username}/{PostURLTests.post.pk}/edit/'
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertRedirects(
                    response, f'/auth/login/?next={url}')

    def test_templates_by_adresses(self):
        username = PostURLTests.user.username
        pk = PostURLTests.post.pk
        template_by_url = {
            '/': 'posts/index.html',
            f'/group/{PostURLTests.group.slug}/': 'posts/group.html',
            '/new/': 'posts/create_post.html',
            f'/{username}/': 'posts/profile.html',
            f'/{username}/{pk}/': 'posts/post_detail.html',
            f'/{username}/{pk}/edit/': 'posts/create_post.html'
        }
        for url, template in template_by_url.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
