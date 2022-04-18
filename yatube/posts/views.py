from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import SlugField
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User


def index(request: HttpRequest) -> HttpResponse:
    """Вернуть HttpResponse объекта главной страницы"""
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "posts/index.html", {'page_obj': page_obj})


def group_posts(request: HttpRequest, slug: SlugField) -> HttpResponse:
    """Вернуть HttpResponse объекта страницы группы"""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {"group": group, "page_obj": page_obj}
    return render(request, "posts/group_list.html", context)


def profile(request, username=None):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "author": author,
        "page_obj": page_obj,
        "paginator": paginator
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    username = post.author
    context = {"post": post, "username": username}
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = datetime.now()
            post.save()
            return redirect('posts:profile', username=post.author.username)
    else:
        form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    username = post.author
    form = PostForm(instance=post)
    text = post.text
    group = post.group
    is_edit = True
    context = {
        "form": form,
        "username": username,
        "text": text,
        "group": group,
        "post_id": post_id,
        "is_edit": is_edit,
    }
    if post.author != request.user:
        return redirect("posts:post_detail", post.pk)
    elif request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid:
            post = form.save(commit=False)
            post.author = request.user
            if form.cleaned_data["group"]:
                group = form.cleaned_data["group"]
            text = form.cleaned_data["text"]
            post.save()
            return redirect("posts:post_detail", post.pk)
    else:
        return render(
            request,
            "posts/create_post.html",
            context
        )
