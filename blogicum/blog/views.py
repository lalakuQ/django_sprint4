from django.db.models.query import QuerySet
from django.shortcuts import render
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.views.generic import DetailView, CreateView, UpdateView
from django.utils import timezone
from .models import Post, Category


User = get_user_model()


class ProfileDetailView(DetailView):
    model = User
    slug_url_kwarg = 'username'
    slug_field = 'username'
    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs):
        username = kwargs['object']
        posts = Post.objects.select_related(
            'author', 'location', 'category').filter(author=username)
        user = User.objects.get(username=username)

        context = {'profile': user,
                   'page_obj': posts}
        return context


class CreatePostView(CreateView):
    pass


class EditProfileView(UpdateView):
    model = User
    template_name = 'blog/profile.html'


def index(request):
    date_now = timezone.now()
    template_name = 'blog/index.html'
    post_list = Post.objects.custom_filter(date_now)[:5]
    context = {
        'post_list': post_list,
    }
    return render(request, template_name, context)


def post_detail(request, pk):
    date_now = timezone.now()
    template_name = 'blog/detail.html'
    try:
        post = Post.objects.custom_filter(date_now).get(pk=pk)
        if not post:
            raise Http404
    except ObjectDoesNotExist:
        raise Http404
    context = {
        'post': post,
    }
    return render(request, template_name, context)


def category_posts(request, category_slug):
    date_now = timezone.now()
    template_name = 'blog/category.html'
    category = Category.objects.get(slug=category_slug)
    post_list = category.posts.custom_filter(date_now)
    if not post_list:
        raise Http404
    context = { 
        'category': category,
        'post_list': post_list,
    }
    return render(request, template_name, context)

