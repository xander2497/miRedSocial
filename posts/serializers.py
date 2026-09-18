from rest_framework import serializers
from .models import *

class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username',read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "author",
            "author_username",
            "content",
            "created_at",
        ]
        read_only_fields = ["id","created_id","author"]


class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username',read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "author_username",
            "content",
            "image",
            "created_at",
            "updated_at",
            "comments",
        ]
        read_only_fields = ["id","created_id","updated_at","author"]