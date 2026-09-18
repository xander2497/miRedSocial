from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User

class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username']


class MessageSerializer(serializers.ModelSerializer):
    author = UserMiniSerializer(source="sender", read_only=True)

    class Meta:
        model = Message
        fields = ['id','author','content','created_at']


class ConversationSerializer(serializers.ModelSerializer):
    partner = serializers.SerializerMethodField()
    last_message_preview = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id','partner','last_message_preview','created_at']

    def get_partner(self, obj):
        request = self.context.get('request')
        if request is None or not hasattr(request, "user"):
            return None
        me = request.user
        other = obj.user2 if obj.user1 == me else obj.user1
        return UserMiniSerializer(other).data
    
    def get_last_message_preview(self,obj):
        last_msg = obj.messages.order_by('-created_at').first()
        if not last_msg:
            return ""
        text = last_msg.content
        return text if len(text) <= 80 else text[:77] + "..."
        
class CreateMessageSerializer(serializers.Serializer):
    content = serializers.CharField(max_length = 1000)
    def validate_content(self,value):
        if not value.strip():
            raise serializers.ValidationError("El mensaje no puede estar vacio")
        return value