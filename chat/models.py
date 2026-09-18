from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Conversation(models.Model):
    user1 = models.ForeignKey(User,on_delete=models.CASCADE,related_name='conversations_user1')
    user2 = models.ForeignKey(User,on_delete=models.CASCADE,related_name='conversations_user2')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1','user2')

    def __str__(self):
        return f"Conversacion entre {self.user1.username} y {self.user2.username}"
    
class Message(models.Model):
    conversation = models.ForeignKey(Conversation,on_delete=models.CASCADE,related_name='messages')
    sender = models.ForeignKey(User,on_delete=models.CASCADE,related_name='sent_messges')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Mensaje de {self.sender.username}"