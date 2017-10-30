from rest_framework import serializers
from .models import Post, Tag, User, UserForm, ProfileForm,Profile
from django_comments.models import Comment
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('subject', 'content', 'author', 'public', 'post_date')
        read_only_fields = (  'author', 'post_date')
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','password','last_login', 'is_superuser', 'username','first_name','last_name','email','date_joined')
        read_only_fields = ( 'id','password','last_login', 'is_superuser', 'date_joined')
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'bio', 'location','uni','year', 'user_id')
        read_only_fields = ('id', 'user_id')
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id',  'user_name', 'user_email', 'user_url','comment','submit_date','ip_address','is_public','user_id')
        read_only_fields = ('id', 'user_name', 'user_email', 'submit_date','user_id')