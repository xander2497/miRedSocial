from django.urls import path
from .api_views import *


app_name = "posts_api"

urlpatterns = [
    path("my/",MyPostsAPIView.as_view(), name='my_posts'),
    path("feed/",FeedPostsAPIView.as_view(),name='feed_posts'),
    path("create/", CreatePostAPIView.as_view(), name='create_post'),
    path("<int:post_id>/comments/create/", CreateCommentAPIView.as_view(),name='create_comment'),
    path("<int:post_id>/comments/",PostCommentAPIView.as_view(),name='post_comments')
]