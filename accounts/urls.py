from django.urls import path
from .views import *

app_name = 'accounts'

urlpatterns = [
    path("login/",login_page,name='login_page'),
    path("profile/",profile_page,name='profile_page'),
    path("register/",register_page,name='register_page'),
    path("profile/edit/",edit_profile_page,name='edit_profile')
]