from django.db.models.base import Model
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.http import Http404
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.views.generic import CreateView, UpdateView, ListView, TemplateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm

User = get_user_model()


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object == self.request.user


class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = 10

    def get_queryset(self):
        date_now = timezone.now()
        user = User.objects.get(username=self.kwargs['username'])

        if self.request.user != user:
            queryset = Post.objects.custom_filter(date_now).filter(
                author=user)
        else:
            queryset = Post.objects.select_related(
                'location', 'category', 'author').filter(
                author=user
            )
        queryset = queryset.order_by('-pub_date')
        return queryset

    def get_context_data(self):
        context = super().get_context_data()
        user = User.objects.get(username=self.kwargs['username'])
        context.update({
            'profile': user,
        })
        return context


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    login_url = '/auth/login/'

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', kwargs={
            'username': self.get_object().username}
        )


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


class CommentCreateView(CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = Post.objects.get(pk=self.get_object().pk)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.get_object().pk})


class CommentUpdateView(UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self):
        return self.request.comment

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = Post.objects.get(pk=self.get_object().pk)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_pk': self.get_object().pk})


class CommentDeleteView(DeleteView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'


class PostDeleteView(DeleteView):
    model = Post


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
    form = CommentForm
    template_name = 'blog/detail.html'
    try:
        post = Post.objects.custom_filter(date_now).get(pk=pk)
        if not post:
            raise Http404
    except ObjectDoesNotExist:
        raise Http404
    context = {
        'post': post,
        'form': form,
        'comments': Comment.objects.filter(post=post).select_related('author')   
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

