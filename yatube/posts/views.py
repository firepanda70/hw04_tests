from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from .forms import PostForm
from .models import Group, Post
from yatube.settings import ELEMENTS_PER_PAGE

User = get_user_model()


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.all()
    paginator = Paginator(posts, ELEMENTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, ELEMENTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'group': group,
        'page': page
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, ELEMENTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {
        'author': author,
        'page': page,
    }
    return render(request, template, context)


def post_detail(request, username, post_id):
    template = 'posts/post_detail.html'
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(author.posts, pk=post_id)
    context = {
        'author': author,
        'post': post
    }
    return render(request, template, context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        Post.objects.create(
            text=form.cleaned_data['text'],
            author=request.user,
            group=form.cleaned_data['group'])
        return redirect('posts:index')
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(author.posts, pk=post_id)
    if request.user != author:
        return redirect('posts:post_detail', author.username, post_id)
    form = PostForm(request.POST or None)
    if request.method == 'GET':
        form.fields['text'].initial = post.text
        form.fields['group'].initial = post.group
        return render(request, 'posts/create_post.html',
                      {'is_edit': True, 'form': form})
    if form.is_valid():
        post.text = form.cleaned_data['text']
        post.group = form.cleaned_data['group']
        post.save()
        return redirect('posts:post_detail', author.username, post_id)
    return render(request, 'posts/create_post.html',
                  {'is_edit': True, 'form': form})
