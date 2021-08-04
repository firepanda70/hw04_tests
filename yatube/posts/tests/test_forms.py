from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group
from posts.forms import PostForm

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='amogus')
        cls.group = Group.objects.create(
            title='Заголовок',
            description='Описание',
            slug='test-slug'
        )
        cls.form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.user)

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст',
            'group-id': 1
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data
        )
        self.assertRedirects(response, reverse('posts:index'))

        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        form_data = {
            'text': 'Обновленный текст',
            'group-id': 1
        }
        Post.objects.create(text='Текст',
                            group=PostCreateFormTests.group,
                            author=PostCreateFormTests.user)
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'username': 'amogus', 'post_id': 1}),
            data=form_data
        )
        self.assertRedirects(response, reverse('posts:post_detail',
                             kwargs={'username': 'amogus', 'post_id': 1}))

        self.assertEqual(Post.objects.get(pk=1).text, form_data['text'])
