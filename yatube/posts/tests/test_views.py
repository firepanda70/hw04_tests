import datetime as dt
from math import ceil

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, Group

User = get_user_model()
# меньше 1 рабоать не будет :)
TASK_COUNT = 15


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='amogus')
        cls.group = Group.objects.create(
            title='Заголовок',
            description='Описание',
            slug='test-slug'
        )
        cls.empty_group = Group.objects.create(
            title='Заголовок',
            description='Описание',
            slug='empty_group'
        )
        for i in range(TASK_COUNT):
            Post.objects.create(
                author=cls.user,
                group=cls.group,
                text='Текст'
            )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Тест на правильность шаблонов
    def test_is_correct_template(self):
        username = PostPagesTest.user.username
        group = PostPagesTest.group.slug
        template_per_page = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group',
                    kwargs={'slug': group}): 'posts/group.html',
            reverse('posts:profile',
                    kwargs={'username': username}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={
                        'username': username,
                        'post_id': 1
                    }): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={
                        'username': username,
                        'post_id': 1
                    }): 'posts/create_post.html',
        }

        for reverse_name, template in template_per_page.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Тест формы создания поста
    def test_post_create_form(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for field_name, value in form_fields.items():
            with self.subTest(field_name=field_name):
                field = response.context['form'].fields[field_name]
                self.assertIsInstance(field, value)

    # Тест формы редактирования поста
    def test_post_edit_form(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'username': 'amogus', 'post_id': 1})
        )
        form_fields = {
            'text': (forms.fields.CharField, 'Текст'),
            'group': (forms.fields.ChoiceField, PostPagesTest.group)
        }

        for field_name, values in form_fields.items():
            with self.subTest(field_name=field_name):
                field = response.context['form'].fields[field_name]
                self.assertIsInstance(field, values[0])
                self.assertEqual(field.initial, values[1])

    # Тест паджинатора
    def test_paginator(self):
        left = TASK_COUNT

        def reqests(page):
            requests = (
                reverse('posts:index') + f'?page={page}',
                reverse('posts:group',
                        kwargs={'slug': PostPagesTest.group.slug}
                        ) + f'?page={page}',
                reverse('posts:profile',
                        kwargs={'username': PostPagesTest.user.username}
                        ) + f'?page={page}'
            )
            for request in requests:
                with self.subTest(request=request):
                    response = self.authorized_client.get(request)
                    self.assertEqual(
                        len(response.context['page'].object_list),
                        min(left, 10)
                    )
        reqests(1)
        if left % 10 != 0:
            last_page = ceil(left / 10)
            left = left % 10
            reqests(last_page)
        else:
            last_page = left / 10
            left = 10
            reqests(last_page)

    # Тест контекста страниц паджинатора
    def test_pages_context(self):
        requests = (
            reverse('posts:index'),
            reverse('posts:group',
                    kwargs={'slug': PostPagesTest.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': PostPagesTest.user.username})
        )
        for request in requests:
            with self.subTest(request=request):
                response = self.authorized_client.get(request)
                post = response.context['page'].object_list[0]
                self.assertEqual(post.text, 'Текст')
                self.assertEqual(post.group_id, 1)
                self.assertEqual(post.author_id, 1)
                self.assertEqual(post.pub_date.date(),
                                 dt.datetime.now().date())

    # Тест контекста детальной информации поста
    def test_detail_post_info(self):
        request = reverse('posts:post_detail',
                          kwargs={'username': 'amogus', 'post_id': 1})
        response = self.authorized_client.get(request)
        post = response.context['post']
        self.assertEqual(post.text, 'Текст')
        self.assertEqual(post.group_id, 1)
        self.assertEqual(post.author_id, 1)
        self.assertEqual(post.pub_date.date(),
                         dt.datetime.now().date())

    # Проверяем, что пустая группа пуста
    def test_empty_group(self):
        request = reverse('posts:group',
                          kwargs={'slug': 'empty_group'})
        response = self.authorized_client.get(request)
        self.assertEqual(
            len(response.context['page'].object_list), 0
        )
