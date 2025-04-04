from rest_framework import serializers
from .models import Post, Comment, Like, Tag
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at', 'updated_at', 'parent', 'replies', 'can_edit']
        read_only_fields = ['user', 'created_at', 'updated_at', 'parent', 'replies']
    
    def get_replies(self, obj):
        replies = Comment.objects.filter(parent=obj).order_by('created_at')
        serializer = CommentSerializer(replies, many=True)
        return serializer.data
    
    def get_can_edit(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.user == request.user
        return False

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'created_at', 'updated_at', 
                 'is_published', 'tags', 'comments', 'likes_count']
        extra_kwargs = {
            'author': {'read_only': True},
        }
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    

class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']