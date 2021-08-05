"""
Модуль предназначен для тестирования urls проекта.
"""

from django.test import Client, TestCase

from posts.models import Group, Post, User

TEST_USER_USERNAME = 'amogus'
TEST_GROUP_TITLE = 'Заголовок'
TEST_GROUP_SLUG = 'test-slug'
TEST_GROUP_DESC = 'Описание'
TEST_POST_TEXT = 'Текст'

STATIC_TEMPLATE_BY_URL_DICT = {
    'homepage': ('/', 'posts/index.html'),
    'new_post': ('/new/', 'posts/create_post.html'),
    'group': (f'/group/{TEST_GROUP_SLUG}/', 'posts/group.html'),
    'profile': (f'/{TEST_USER_USERNAME}/', 'posts/profile.html'),
}


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username=TEST_USER_USERNAME)
        cls.group = Group.objects.create(
            title=TEST_GROUP_TITLE,
            description=TEST_GROUP_DESC,
            slug=TEST_GROUP_SLUG
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text=TEST_POST_TEXT
        )

    def get_template_urls_by_name(self, name):
        """
        Функция для удобного доступа к парам ссылка-шаблон.
        """

        def post_detail():
            return (
                f'/{TEST_USER_USERNAME}/{PostURLTests.post.pk}/',
                'posts/post_detail.html'
            )

        def post_edit():
            return (
                f'/{TEST_USER_USERNAME}/{PostURLTests.post.pk}/edit/',
                'posts/create_post.html'
            )

        dynamic_urls = {
            'post_edit': post_edit(),
            'post_detail': post_detail()
        }

        if name in STATIC_TEMPLATE_BY_URL_DICT:
            return STATIC_TEMPLATE_BY_URL_DICT[name]
        return dynamic_urls[name]

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)

    def test_urls_access_from_anonimous_user(self):
        """
        Тест проверяет доступность страниц для анонимного пользователя.
        """

        urls_names = (
            'homepage',
            'group',
            'profile',
            'post_detail'
        )
        for name in urls_names:
            url = self.get_template_urls_by_name(name)[0]
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200,
                                 f'fail at getting to "{url}" page')

    def test_urls_access_from_authorised_user(self):
        """
        Тест проверяет доступность страниц для авторизованного пользователя.
        """

        urls_names = (
            'new_post',
            'post_edit'
        )
        for name in urls_names:
            url = self.get_template_urls_by_name(name)[0]
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, 200,
                                 f'fail at getting to "{url}" page')

    def test_redirect_for_anonimous_user(self):
        """
        Тест проверяет редиректы со страниц для анонимного пользователя.
        """

        urls_names = (
            'new_post',
            'post_edit'
        )
        for name in urls_names:
            url = self.get_template_urls_by_name(name)[0]
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertRedirects(
                    response, f'/auth/login/?next={url}')

    def test_templates_by_adresses(self):
        """
        Тест проверяет, что страницы используют правильные шаблоны.
        """

        urls_names = (
            'homepage',
            'group',
            'profile',
            'post_detail',
            'new_post',
            'post_edit'
        )
        for name in urls_names:
            url, template = self.get_template_urls_by_name(name)
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
