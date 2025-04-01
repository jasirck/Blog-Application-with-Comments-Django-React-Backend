from django.urls import path
from . import views

urlpatterns = [
    path('posts/', views.PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', views.PostRetrieveUpdateDestroyView.as_view(), name='post-detail'),
    path('posts/<int:post_id>/comments/', views.CommentListCreateView.as_view(), name='comment-list'),
    path('comments/<int:comment_id>/', views.CommentDetailView.as_view(), name='comment-detail'),
    path('comments/<int:comment_id>/reply/', views.ReplyCreateView.as_view(), name='comment-reply'),
    path('posts/<int:post_id>/like/', views.LikeCreateDestroyView.as_view(), name='post-like'),
    path('tags/', views.TagListView.as_view(), name='tag-list'),
]