import datetime as dt

from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Отряды Понасенкова',
            slug='genius',
            description='Аниме-клуб'
        )

    def test_verbose_name_and_help_text(self):
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
        group = GroupModelTest.group
        expected = group.title
        self.assertEqual(str(group), expected)


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = User.objects.create_user(
            first_name='Евгений',
            last_name='Понасенков',
            username='ponasenkov',
        )
        cls.group = Group.objects.create(
            title='Отряды Понасенкова',
            slug='genius',
            description='Аниме-клуб'
        )
        cls.post = Post.objects.create(
            text='Гений ' * 10,
            author=cls.user,
            group=cls.group
        )

    def test_verbose_name_and_help_text(self):
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
        post = PostModelTest.post
        text = ('Автор: Евгений Понасенков (ponasenkov)\n'
                'Группа: Отряды Понасенкова\n'
                f'Дата публикации: {str(dt.datetime.now().date())}\n'
                'Текст: Гений Гений Гений...'
                )
        self.assertEqual(str(post), text)
