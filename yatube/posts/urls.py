from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.index, name='index'),
    path('group/<slug:slug>/', views.group_posts, name='group'),
    path('new/', views.post_create, name='post_create'),
    path('<username>/', views.profile, name='profile'),
    path('<username>/<int:post_id>/', views.post_detail, name='post_detail'),
    path('<username>/<int:post_id>/edit/', views.post_edit, name='post_edit')
]
