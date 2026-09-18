from django.urls import path
from .api_views import *
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

app_name="accounts_api"

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name='register'),
    path("login/", TokenObtainPairView.as_view(), name='login'),
    path("refresh/", TokenRefreshView.as_view(), name='refresh'),
    path("me/", MeAPIView.as_view(), name='me'),
    path("profile/update/", UpdateProfileView.as_view(), name='profile_update'),
    path("users/",UserListAPIView.as_view(),name='user_list')
]