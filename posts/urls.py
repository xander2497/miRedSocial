from django.urls import path
from .views import *

app_name = 'posts'

urlpatterns = [
    path("feed/", feed_page, name='feed_page')
]