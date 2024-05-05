from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from django.http import Http404, Http404
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.utils import timezone
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm, UserForm
from .mixins import (
    CustomLoginRequiredMixin,
    OnlyPostAuthorMixin,
    ProfileMixin,
    PostMixin,
    PostFormMixin,
    OnlyCommentAuthorMixin,
    CommentFormMixin
)
from .utils import get_page_obj


User = get_user_model()


class PostCreateView(CustomLoginRequiredMixin, PostFormMixin, CreateView):
    pass


class PostUpdateView(OnlyPostAuthorMixin, PostFormMixin, UpdateView):
    pass


class PostDeleteView(OnlyPostAuthorMixin, PostMixin, DeleteView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'form': PostForm(instance=self.object)
        })

        return context


class ProfileListView(ProfileMixin, ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = 10
    user = None

    def get_queryset(self):
        date_now = timezone.now()
        self.user = get_object_or_404(User, username=self.kwargs['username'])
        if self.request.user != self.user:
            queryset = Post.objects.custom_filter(date_now).filter(
                author=self.user).annotate(
                    comment_count=Count('comments')).order_by('-pub_date')
        else:
            queryset = Post.objects.select_related(
                'location', 'category', 'author').filter(
                author=self.user
            ).annotate(comment_count=Count('comments')).order_by('-pub_date')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'profile': self.user,
        })
        return context


class ProfileUpdateView(CustomLoginRequiredMixin, ProfileMixin, UpdateView):
    template_name = 'blog/user.html'
    form_class = UserForm

    def get_success_url(self):
        return reverse('blog:profile', kwargs={
            'username': self.get_object().username}
        )


class CommentCreateView(CustomLoginRequiredMixin,
                        CommentFormMixin,
                        CreateView):
    pass


class CommentUpdateView(OnlyCommentAuthorMixin,
                        CommentFormMixin,
                        UpdateView):
    pass


class CommentDeleteView(OnlyCommentAuthorMixin,
                        CommentFormMixin,
                        DeleteView):

    pass


def index(request):
    date_now = timezone.now()
    template_name = 'blog/index.html'
    post_list = Post.objects.custom_filter(date_now).annotate(
        comment_count=Count('comments')).order_by('-pub_date')
    page_obj = get_page_obj(post_list, request)
    context = {
        'page_obj': page_obj,
        'comment_count': post_list.values('comment_count'),
    }
    return render(request, template_name, context)


def post_detail(request, post_pk):
    date_now = timezone.now()
    template_name = 'blog/detail.html'
    form = CommentForm()

    post = get_object_or_404(Post.objects.select_related('author'),
                             pk=post_pk)

    if (post.pub_date > date_now or not post.is_published) and (
            request.user != post.author):
        raise Http404
    context = {
        'post': post,
        'form': form,
        'comments': Comment.objects.select_related('author').filter(
            post=post).order_by('created_at')
    }
    return render(request, template_name, context)


def category_posts(request, category_slug):
    date_now = timezone.now()
    template_name = 'blog/category.html'
    category = get_object_or_404(Category, slug=category_slug)
    if not category.is_published:
        raise Http404
    post_list = category.posts.custom_filter(date_now).annotate(
        comment_count=Count('comments')).order_by('-pub_date')
    page_obj = get_page_obj(post_list, request)
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, template_name, context)
