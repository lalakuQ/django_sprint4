from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.http import Http404
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.views.generic import DetailView, CreateView, UpdateView, ListView, TemplateView
from django.views.generic.list import MultipleObjectMixin
from django.utils import timezone
from .models import Post, Category
from .forms import CreateForm

User = get_user_model()


class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = 10

    def get_queryset(self):
        queryset = Post.objects.select_related(
            'author', 'location', 'category').filter(
                author__username=self.kwargs['username']).order_by('-pub_date')

        return queryset

    def get_context_data(self):
        context = super().get_context_data()
        user = User.objects.get(username=self.kwargs['username'])
        context.update({
            'profile': user,
        })
        return context


class CreatePostView(CreateView):
    model = Post
    form_class = CreateForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class ProfileUpdateView(UpdateView):
    template_name = 'blog/user.html'
    fields = ('username',
              'first_name',
              'last_name',
              'email')

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile', kwargs={
            'username': self.get_object().username})


def index(request):
    date_now = timezone.now()
    template_name = 'blog/index.html'
    post_list = Post.objects.custom_filter(date_now)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
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
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    if not post_list:
        raise Http404
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, template_name, context)

