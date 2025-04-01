from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.models import User
from django.db import models
from .models import Post, Comment, Like, Tag
from .serializers import PostSerializer, CommentSerializer, LikeSerializer, TagSerializer ,TagSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

class PostListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        queryset = Post.objects.filter(is_deleted=False)
        
        author_id = request.query_params.get('author')
        if author_id:
            queryset = queryset.filter(author_id=author_id)
            
        is_published = request.query_params.get('is_published')
        if is_published:
            queryset = queryset.filter(is_published=is_published.lower() == 'true')
            
        tags = request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__id__in=tags).distinct()
        
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search) | 
                models.Q(content__icontains=search)
            )
            
        serializer = PostSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        data = request.data.copy()
        tags_data = data.pop('tags', [])
        
        serializer = PostSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            post = serializer.save(author=request.user)
            
            # Handle tags
            tag_instances = []
            for tag_name in tags_data:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                tag_instances.append(tag)
            
            post.tags.set(tag_instances)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostRetrieveUpdateDestroyView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk, is_deleted=False)
        except Post.DoesNotExist:
            return None
    
    def get(self, request, pk):
        post = self.get_object(pk)
        if not post:
            return Response(
                {'detail': 'Post not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = PostSerializer(post)
        return Response(serializer.data)
    
    def put(self, request, pk):
        post = self.get_object(pk)
        if not post:
            return Response(
                {'detail': 'Post not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if post.author != request.user:
            return Response(
                {'detail': 'You do not have permission to perform this action.'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        post = self.get_object(pk)
        if not post:
            return Response(
                {'detail': 'Post not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if post.author != request.user:
            return Response(
                {'detail': 'You do not have permission to perform this action.'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        post.is_deleted = True
        post.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CommentListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_post(self, post_id):
        try:
            return Post.objects.get(pk=post_id, is_deleted=False)
        except Post.DoesNotExist:
            return None
    
    def get(self, request, post_id):
        post = self.get_post(post_id)
        if not post:
            return Response(
                {'detail': 'Post not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        comments = Comment.objects.filter(post=post, parent__isnull=True)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    def post(self, request, post_id):
        post = self.get_post(post_id)
        if not post:
            return Response(
                {'detail': 'Post not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReplyCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_parent_comment(self, comment_id):
        try:
            return Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            return None
    
    def post(self, request, comment_id):
        parent_comment = self.get_parent_comment(comment_id)
        if not parent_comment:
            return Response(
                {'detail': 'Comment not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                user=request.user,
                post=parent_comment.post,
                parent=parent_comment
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LikeCreateDestroyView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_post(self, post_id):
        try:
            return Post.objects.get(pk=post_id, is_deleted=False)
        except Post.DoesNotExist:
            return None
    
    def post(self, request, post_id):
        post = self.get_post(post_id)
        if not post:
            return Response(
                {'detail': 'Post not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        like, created = Like.objects.get_or_create(
            user=request.user,
            post=post
        )
        
        if not created:
            return Response(
                {'detail': 'You have already liked this post.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        serializer = LikeSerializer(like)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def delete(self, request, post_id):
        post = self.get_post(post_id)
        if not post:
            return Response(
                {'detail': 'Post not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        try:
            like = Like.objects.get(user=request.user, post=post)
            like.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Like.DoesNotExist:
            return Response(
                {'detail': 'You have not liked this post.'},
                status=status.HTTP_400_BAD_REQUEST
            )

class TagListView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)