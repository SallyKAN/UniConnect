from django.db import models
from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_comments.signals import comment_was_posted

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


def notify_followers(comment, request, **kwargs):
    post = Post.objects.get(pk=comment.object_pk)
    for follower in post.followers.all():
        text = "New comment on your post" if (follower == post.author) else "New comment on a post you follow"
        n = Notification(owner=follower, post=post, text=text)
        n.save()


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'location', 'birth_date')


class Post(models.Model):
    subject = models.CharField(max_length=160)
    content = models.CharField(max_length=800)
    author = models.ForeignKey(User, related_name='user_author', on_delete=models.CASCADE)
    public = models.BooleanField(default=False)
    post_date = models.DateTimeField(auto_now_add=True)
    followers = models.ManyToManyField(User, related_name='user_followers')


class Notification(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.CharField(max_length=36,default="New comment on a post you follow")


class Tag(models.Model):
    # We will use the implcit id
    tag = models.CharField(max_length=10, unique=True)
    creation_date = models.DateTimeField(auto_now_add=True)


class PostTag(models.Model):
    post = models.ForeignKey(Post)
    tag = models.ForeignKey(Tag)


comment_was_posted.connect(notify_followers)
