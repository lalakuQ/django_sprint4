from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from .forms import PostForm, CommentForm
from .models import Post, Comment


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


class ProfileMixin:
    def get_object(self):
        return self.request.user


class PostMixin:
    model = Post
    template_name = 'blog/create.html'

    def get_user(self):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile', kwargs={
            'username': self.get_user().username}
        )


class PostFormMixin(PostMixin):
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.get_user()
        return super().form_valid(form)


class OnlyCommentAuthorMixin(UserPassesTestMixin):
    def get_object(self):
        comment = get_object_or_404(Comment, pk=self.kwargs['comment_pk'])
        return comment

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class CommentMixin:
    model = Comment
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(Post, pk=self.kwargs['post_pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_obj
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={
            'post_pk': self.kwargs['post_pk']
        })


class CommentFormMixin(CommentMixin):
    form_class = CommentForm
