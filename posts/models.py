from django.db import models
from django.contrib.auth.models import User

###  u1.post_set.all() -> u1.posts.all()
###  p1.author
# Create your models here.
class Post(models.Model):
    author = models.ForeignKey(User,on_delete=models.CASCADE,related_name="posts")
    content = models.TextField(max_length=500)
    image = models.ImageField(upload_to="posts/",blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Post de {self.author.username} - {self.created_at.strftime('%Y-%m-%d')}"
    

class Comment(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='comments')
    author = models.ForeignKey(User,on_delete=models.CASCADE)
    content = models.TextField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentario de {self.author.username} - {self.created_at.strftime('%Y-%m-%d')}"