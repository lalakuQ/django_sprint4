from django.urls import path
from . import views


app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),
    path('posts/create/', views.CreatePostView.as_view(), name='create_post'),
    path('category/<slug:category_slug>/', views.category_posts,
         name='category_posts'),
    path('profile/<slug:username>/', views.ProfileListView.as_view(),
         name='profile'),
    path('profile/edit/', views.EditProfileView.as_view(),
         name='edit_profile'),
]
