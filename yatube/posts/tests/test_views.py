"""
Модуль предназначен для тестирования view-функций.
"""

import datetime as dt
from math import ceil

from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

# меньше 1 рабоать не будет :)
POSTS_COUNT = 15
POST_PER_PAGE_COUNT = 10

TEST_USER_USERNAME = 'amogus'
TEST_GROUP_TITLE = 'Заголовок'
TEST_GROUP_SLUG = 'test-slug'
TEST_GROUP_DESC = 'Описание'
TEST_POST_TEXT = 'Текст'
TEST_EMPTY_GROUP_SLUG = 'empty_group'

REQUEST_TEMPLATE_DICT = {
    'homepage': (reverse('posts:index'), 'posts/index.html'),
    'new_post': (reverse('posts:post_create'), 'posts/create_post.html'),
    'group': (reverse('posts:group',
                      kwargs={
                          'slug': TEST_GROUP_SLUG
                      }), 'posts/group.html'),
    'empty_group': (reverse('posts:group',
                            kwargs={
                                'slug': TEST_EMPTY_GROUP_SLUG
                            }), 'posts/group.html'),
    'profile': (reverse('posts:profile',
                        kwargs={
                            'username': TEST_USER_USERNAME
                        }), 'posts/profile.html'),
    'post_edit': (reverse('posts:post_edit',
                          kwargs={
                              'username': TEST_USER_USERNAME,
                              'post_id': POSTS_COUNT
                          }), 'posts/create_post.html'),
    'post_detail': (reverse('posts:post_detail',
                            kwargs={
                                'username': TEST_USER_USERNAME,
                                'post_id': POSTS_COUNT
                            }), 'posts/post_detail.html')
}


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username=TEST_USER_USERNAME)
        cls.group = Group.objects.create(
            title=TEST_GROUP_TITLE,
            description=TEST_GROUP_DESC,
            slug=TEST_GROUP_SLUG
        )
        cls.empty_group = Group.objects.create(
            title=TEST_GROUP_TITLE,
            description=TEST_GROUP_DESC,
            slug=TEST_EMPTY_GROUP_SLUG
        )
        posts = [
            Post(author=cls.user, group=cls.group, text=TEST_POST_TEXT)
        ] * POSTS_COUNT
        Post.objects.bulk_create(posts)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_is_correct_template(self):
        """
        Тест проверяет, что view-функции используют правильные html шаблоны.
        """

        view_names = (
            'homepage',
            'group',
            'profile',
            'post_detail',
            'new_post',
            'post_edit',
        )

        for view_name in view_names:
            reverse_name, template = REQUEST_TEMPLATE_DICT[view_name]
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_create_form(self):
        """
        Тест проверяет, что форма создания поста имеет ожидаемые поля ввода.
        """

        request = REQUEST_TEMPLATE_DICT['new_post'][0]
        response = self.authorized_client.get(request)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for field_name, value in form_fields.items():
            with self.subTest(field_name=field_name):
                field = response.context['form'].fields[field_name]
                self.assertIsInstance(field, value)

    def test_post_edit_form(self):
        """
        Тест проверяет, что форма редактирования поста заполнена
        актуальными значениями.
        """

        request = REQUEST_TEMPLATE_DICT['post_edit'][0]
        response = self.authorized_client.get(request)
        form_fields = {
            'text': (forms.fields.CharField, TEST_POST_TEXT),
            'group': (forms.fields.ChoiceField, PostPagesTest.group)
        }

        for field_name, values in form_fields.items():
            with self.subTest(field_name=field_name):
                field = response.context['form'].fields[field_name]
                self.assertIsInstance(field, values[0])
                self.assertEqual(field.initial, values[1])

    def test_paginator(self):
        """
        Тест проверяет, что страица содержит ожидаемое количество
        элементов.
        """

        left = POSTS_COUNT

        def reqests(page):
            view_names = (
                'homepage',
                'group',
                'profile',
            )
            for view_name in view_names:
                request = REQUEST_TEMPLATE_DICT[view_name][0] + f'?page={page}'
                with self.subTest(request=request):
                    response = self.authorized_client.get(request)
                    self.assertEqual(
                        len(response.context['page'].object_list),
                        min(left, POST_PER_PAGE_COUNT)
                    )
        reqests(1)
        if left % POST_PER_PAGE_COUNT != 0:
            last_page = ceil(left / POST_PER_PAGE_COUNT)
            left = left % POST_PER_PAGE_COUNT
            reqests(last_page)
        else:
            last_page = left / POST_PER_PAGE_COUNT
            left = POST_PER_PAGE_COUNT
            reqests(last_page)

    def test_pages_context(self):
        """
        Тест проверяет контекст страниц паджинатора.
        """

        view_names = (
            'homepage',
            'group',
            'profile'
        )
        for view_name in view_names:
            request = REQUEST_TEMPLATE_DICT[view_name][0]
            with self.subTest(request=request):
                response = self.authorized_client.get(request)
                post = response.context['page'].object_list[0]
                self.assertEqual(post.text, TEST_POST_TEXT)
                self.assertEqual(post.group.title, TEST_GROUP_TITLE)
                self.assertEqual(post.author.username, TEST_USER_USERNAME)
                self.assertEqual(post.pub_date.date(),
                                 dt.datetime.now().date())

    def test_detail_post_info(self):
        """
        Тест проверяет контекст страницы детальной информации поста.
        """

        request = REQUEST_TEMPLATE_DICT['post_detail'][0]
        response = self.authorized_client.get(request)
        post = response.context['post']
        self.assertEqual(post.text, TEST_POST_TEXT)
        self.assertEqual(post.group.title, TEST_GROUP_TITLE)
        self.assertEqual(post.author.username, TEST_USER_USERNAME)
        self.assertEqual(post.pub_date.date(),
                         dt.datetime.now().date())

    def test_empty_group(self):
        """
        Тест проверяет, что в пустой группе нет постов.
        """

        request = REQUEST_TEMPLATE_DICT['empty_group'][0]
        response = self.authorized_client.get(request)
        self.assertEqual(
            len(response.context['page'].object_list), 0
        )
