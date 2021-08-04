import textwrap

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        'Заголовок',
        max_length=200,
        help_text='Название группы'
    )
    slug = models.SlugField('Адрес', unique=True, help_text='Адрес группы')
    description = models.TextField('Описание', help_text='Описание группы')

    class Meta:
        verbose_name = 'Группа'

    def __str__(self):
        return str(self.title)


class Post(models.Model):
    text = models.TextField('Текст', help_text='Текст поста')
    pub_date = models.DateTimeField(
        'Дата пуликации',
        auto_now_add=True,
        help_text='Дата публикации поста'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='posts',
        help_text='Автор поста'
    )
    group = models.ForeignKey(
        Group,
        verbose_name='Группа',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        help_text='Связанная группа'
    )

    class Meta:
        ordering = ('-pub_date', )
        verbose_name = 'Пост'

    def __str__(self):
        fullname = self.author.get_full_name()
        slug = self.author.username
        res = f'Автор: {fullname} ({slug})\n'
        res += f'Группа: {self.group}\n'
        res += f'Дата публикации: {self.pub_date.date()}\n'
        shorten_text = textwrap.shorten(
            text=self.text,
            width=20,
            placeholder="..."
        )
        res += f'Текст: {shorten_text}'
        return res
        # return self.text[0:15]
        # return textwrap.shorten(text=self.text, width=15)
