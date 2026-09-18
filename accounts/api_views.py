from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import *
from .serializers import *


class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=200)


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username',"").strip()
        email = request.data.get('email',"").strip()
        password = request.data.get('password',"")
        password2 = request.data.get('password2',"")

        if not username or not email or not password or not password2:
            return Response(
                {"error": "Todos los campos son obligatorios"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if password != password2:
            return Response(
                {"error": "Las contraseñas no coinciden"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            validate_password(password)
        except DjangoValidationError as e:
            return Response(
                {"error": list(e.messages)},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "El nombre de usuario ya esta en uso"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email__iexact=email).exists():
            return Response(
                {"error": "El email ya esta registrado"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        Profile.objects.create(user=user)

        serializer = UserSerializer(user)

        return Response(serializer.data,status=status.HTTP_201_CREATED)
    
class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self,request):
        user = request.user
        profile = user.profile

        user.first_name = request.data.get('first_name',user.first_name)
        user.last_name = request.data.get('last_name',user.last_name)
        profile.bio = request.data.get('bio',profile.bio)
        profile.birthdate = request.data.get('birthdate',profile.birthdate)
        is_private_raw = request.data.get('is_private', profile.is_private)
        if str(is_private_raw).lower() == 'true':
            profile.is_private = True
        else:
            profile.is_private = False

        avatar = request.FILES.get('avatar')
        if avatar:
            profile.avatar = avatar

        user.save()
        profile.save()
        return Response({"updated": True},status=200)
    
class UserListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        queryset = User.objects.exclude(id=request.user.id)
        serializer = UserSerializer(queryset,many=True)
        return Response(serializer.data, status=200)