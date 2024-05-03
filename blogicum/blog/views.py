from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.http import Http404, Http404
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm, UserForm

User = get_user_model()


class CustomLoginRequiredMixin(LoginRequiredMixin):
    login_url = '/auth/login'


class OnlyPostAuthorMixin(UserPassesTestMixin):
    def get_object(self):
        post_pk = self.kwargs.get('post_pk')
        post_object = get_object_or_404(Post.objects.select_related(
            'location', 'category', 'author', ),
            pk=post_pk
        )
        return post_object

    def test_func(self):
        object = get_object_or_404(
            Post.objects.select_related('author'),
            pk=self.kwargs['post_pk']
        )
        return object.author == self.request.user

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_pk=self.kwargs['post_pk'])


class PostMixin:
    model = Post
    template_name = 'blog/create.html'

    def get_user(self):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile', kwargs={
            'username': self.request.user.username}
        )


class PostFormMixin(PostMixin):
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.get_user()
        return super().form_valid(form)


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


class ProfileMixin:
    def get_object(self):
        return self.request.user


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


class OnlyCommentAuthorMixin(UserPassesTestMixin):
    def get_object(self):
        comment = get_object_or_404(Comment, pk=self.kwargs['comment_pk'])
        return comment

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class CommentMixin:
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={
            'post_pk': self.kwargs['post_pk']
        })


class CommentFormMixin:
    form_class = CommentForm


class CommentCreateView(CustomLoginRequiredMixin,
                        CommentMixin,
                        CommentFormMixin,
                        CreateView):

    def get(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(Post, pk=self.kwargs['post_pk'])
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_pk'])
        return super().form_valid(form)


class CommentUpdateView(OnlyCommentAuthorMixin,
                        CommentMixin,
                        CommentFormMixin,
                        UpdateView):

    def form_valid(self, form):
        form.instance.comment = self.get_object()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'comment': self.get_object()
        })
        return context


class CommentDeleteView(OnlyCommentAuthorMixin, CommentMixin, DeleteView):
    model = Comment
    form_class = CommentForm


def index(request):
    date_now = timezone.now()
    template_name = 'blog/index.html'
    post_list = Post.objects.custom_filter(date_now).annotate(
        comment_count=Count('comments')).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
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
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, template_name, context)
