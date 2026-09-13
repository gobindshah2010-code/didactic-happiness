from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from .forms import NewsArticleForm
from .models import NewsArticle


def user_in_group(user, group_name):
    return user.is_authenticated and user.groups.filter(name=group_name).exists()


def can_publish(user):
    return (
        user.is_superuser
        or user_in_group(user, "Publisher")
        or user_in_group(user, "Admin")
    )


def can_create_article(user):
    return (
        user.is_superuser
        or user_in_group(user, "Editor")
        or user_in_group(user, "Publisher")
        or user_in_group(user, "Admin")
    )


def can_edit_article(user, article):
    if user.is_superuser:
        return True

    if article.author == user and user_in_group(user, "Editor"):
        return True

    if user_in_group(user, "Publisher") or user_in_group(user, "Admin"):
        return True

    return False


def article_list(request):
    articles = NewsArticle.objects.filter(status=NewsArticle.PUBLISHED)

    return render(
        request,
        "articles/article_list.html",
        {"articles": articles}
    )


def article_detail(request, slug):
    article = get_object_or_404(NewsArticle, slug=slug)

    if article.status != NewsArticle.PUBLISHED:
        if not request.user.is_authenticated:
            raise PermissionDenied

        if not (
            article.author == request.user
            or can_publish(request.user)
            or request.user.is_superuser
        ):
            raise PermissionDenied

    return render(
        request,
        "articles/article_detail.html",
        {"article": article}
    )


@login_required
def article_create(request):
    if not can_create_article(request.user):
        raise PermissionDenied

    form = NewsArticleForm(
        request.POST or None,
        request.FILES or None
    )

    if request.method == "POST" and form.is_valid():
        article = form.save(commit=False)
        article.author = request.user

        action = request.POST.get("action")

        if action == "publish" and can_publish(request.user):
            article.status = NewsArticle.PUBLISHED

        elif action == "submit":
            article.status = NewsArticle.PENDING

        else:
            article.status = NewsArticle.DRAFT

        article.save()

        if article.status == NewsArticle.PUBLISHED:
            message = "Published"
        elif article.status == NewsArticle.PENDING:
            message = "Sent for review"
        else:
            message = "Saved as draft"

        messages.success(
            request,
            f"Article “{article.title}” {message}."
        )

        return redirect(article.get_absolute_url())

    return render(
        request,
        "articles/article_form.html",
        {
            "form": form,
            "operation": "Create",
        }
    )


@login_required
def article_edit(request, slug):
    article = get_object_or_404(NewsArticle, slug=slug)

    if not can_edit_article(request.user, article):
        raise PermissionDenied

    form = NewsArticleForm(
        request.POST or None,
        request.FILES or None,
        instance=article
    )

    if request.method == "POST" and form.is_valid():
        article = form.save(commit=False)

        action = request.POST.get("action")

        if action == "publish":
            if not can_publish(request.user):
                raise PermissionDenied

            article.status = NewsArticle.PUBLISHED

        elif action == "submit":
            article.status = NewsArticle.PENDING

        else:
            article.status = NewsArticle.DRAFT

        article.save()

        messages.success(
            request,
            "Article updated."
        )

        return redirect(article.get_absolute_url())

    return render(
        request,
        "articles/article_form.html",
        {
            "form": form,
            "operation": "Edit",
            "article": article,
        }
    )


@login_required
def pending_articles(request):
    if not can_publish(request.user):
        raise PermissionDenied

    articles = NewsArticle.objects.filter(
        status=NewsArticle.PENDING
    )

    return render(
        request,
        "articles/pending_list.html",
        {"articles": articles}
    )


@login_required
def publish_article(request, slug):
    if not can_publish(request.user):
        raise PermissionDenied

    article = get_object_or_404(
        NewsArticle,
        slug=slug
    )

    article.status = NewsArticle.PUBLISHED
    article.save()

    messages.success(
        request,
        f"Article “{article.title}” has been published."
    )

    return redirect("pending_articles")


@login_required
def my_articles(request):
    articles = NewsArticle.objects.filter(
        author=request.user
    )

    return render(
        request,
        "articles/article_list.html",
        {
            "articles": articles,
            "heading": "My Articles",
        }
    )