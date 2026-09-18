from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import *
from .serializers import *

class CreatePostAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        content = request.data.get("content",'')
        image = request.FILES.get("image")

        if not content and not image:
            return Response(
                {"error": "El post debe tener texto o imagen"},
                status = status.HTTP_400_BAD_REQUEST
            )
        
        post = Post.objects.create(
            author = request.user,
            content = content,
            image = image
        )

        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class FeedPostsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        posts = Post.objects.all().order_by("-created_at")
        serializer = PostSerializer(posts,many=True)
        return Response(serializer.data, status=200)


class MyPostsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        posts = Post.objects.filter(author=request.user).order_by("-created_at")
        serializer = PostSerializer(posts,many=True)
        return Response(serializer.data, status=200)
    
class CreateCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request,post_id):
        content = request.data.get("content",'')

        if not content:
            return Response(
                {"error": "El comentario no puede estar vacio"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response(
                {'error': "Post no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )

        comment = Comment.objects.create(
            post=post,
            author=request.user,
            content=content
        )
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class PostCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request,post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response(
                {'error': "Post no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )

        comments = post.comments.all().order_by("created_at")
        serializer = CommentSerializer(comments, many=True)

        return Response(serializer.data)