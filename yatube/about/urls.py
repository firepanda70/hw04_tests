from django.urls import path

from . import views

app_name = 'about'

urlpatterns = [
    path('author/', views.AboutMePage.as_view(), name='me'),
    path('tech/', views.TechPage.as_view(), name='tech'),
]
