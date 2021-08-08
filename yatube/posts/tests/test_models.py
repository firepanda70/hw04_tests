"""
Модуль предназначен для тестирования моделей проекта.
"""

import datetime as dt
import textwrap

from django.test import TestCase

from posts.models import Group, Post, User

TEST_GROUP_TITLE = 'Отряды Понасенкова'
TEST_GROUP_SLUG = 'genius'
TEST_GROUP_DESC = 'Аниме-клуб'
TEST_USER_FIRSTNAME = 'Евгений'
TEST_USER_LASTNAME = 'Понасенков'
TEST_USER_USERNAME = 'ponasenkov'

TEST_POST_TEXT = 'Гений ' * 10

TEST_POST_STR_FUNC_FORMAT = (
    f'Автор: {TEST_USER_FIRSTNAME} {TEST_USER_LASTNAME} '
    f'({TEST_USER_USERNAME})\n'
    f'Группа: {TEST_GROUP_TITLE}\n'
    f'Дата публикации: {dt.datetime.now().date()}\nТекст: '
    f'{textwrap.shorten( text=TEST_POST_TEXT, width=20, placeholder="..." )}'
)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title=TEST_GROUP_TITLE,
            slug=TEST_GROUP_SLUG,
            description=TEST_GROUP_DESC
        )

    def test_verbose_name_and_help_text(self):
        """
        Тест проверяет корректность значений полей verbose_name и
        help_text.
        """

        group = GroupModelTest.group
        fields = {
            'title': ('Заголовок', 'Название группы'),
            'slug': ('Адрес', 'Адрес группы'),
            'description': ('Описание', 'Описание группы')
        }
        for value, expected in fields.items():
            with self.subTest(value=value):
                field = group._meta.get_field(value)
                self.assertEqual(field.verbose_name, expected[0])
                self.assertEqual(field.help_text, expected[1])

    def test_str_method(self):
        """
        Тест проверяет поведение функции str модели Group.
        """

        group = GroupModelTest.group
        expected = group.title
        self.assertEqual(str(group), expected)


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = User.objects.create_user(
            first_name=TEST_USER_FIRSTNAME,
            last_name=TEST_USER_LASTNAME,
            username=TEST_USER_USERNAME,
        )
        cls.group = Group.objects.create(
            title=TEST_GROUP_TITLE,
            slug=TEST_GROUP_SLUG,
            description=TEST_GROUP_DESC
        )
        cls.post = Post.objects.create(
            text=TEST_POST_TEXT,
            author=cls.user,
            group=cls.group
        )

    def test_verbose_name_and_help_text(self):
        """
        Тест проверяет значения полей verbose_name и
        help_text модели Post.
        """

        post = PostModelTest.post
        fields = {
            'text': ('Текст', 'Текст поста'),
            'pub_date': ('Дата пуликации', 'Дата публикации поста'),
            'author': ('Автор', 'Автор поста'),
            'group': ('Группа', 'Связанная группа')
        }
        for field_name, expected_values in fields.items():
            with self.subTest(value=field_name):
                field = post._meta.get_field(field_name)
                self.assertEqual(field.verbose_name, expected_values[0])
                self.assertEqual(field.help_text, expected_values[1])

    def test_str_method(self):
        """
        Тест проверяет работу функции str.
        """

        post = PostModelTest.post
        text = TEST_POST_STR_FUNC_FORMAT
        self.assertEqual(str(post), text)
