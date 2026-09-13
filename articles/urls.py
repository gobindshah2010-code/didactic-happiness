from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.article_list, name='article_list'),
    path('articles/create/', views.article_create, name='article_create'),
    path('articles/mine/', views.my_articles, name='my_articles'),
    path('articles/pending/', views.pending_articles, name='pending_articles'),
    path('articles/<slug:slug>/', views.article_detail, name='article_detail'),
    path('articles/<slug:slug>/edit/', views.article_edit, name='article_edit'),
    path('articles/<slug:slug>/publish/', views.publish_article, name='publish_article'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='article_list'), name='logout'),
]
