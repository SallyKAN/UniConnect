from django.db import models
from django.forms import ModelForm
from django import forms
import random
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_comments.signals import comment_was_posted
from django.core.urlresolvers import reverse

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, default='Lorem ipsum dolor sit amet, consectetur adipiscing elit.')
    location = models.CharField(max_length=30, default="AU")
    date_joined = models.DateField(auto_now_add=True)
    uni = models.CharField(max_length=30, default='University of Sydney')
    year = models.CharField(max_length=10, default="3")
    profics = models.IntegerField(default = random.randint(0,1))
    pict = models.CharField(max_length=30, blank=True)

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
        fields = ('bio', 'location', 'uni', 'pict', 'year')


class Tag(models.Model):
    # We will use the implcit id
    tag = models.CharField(max_length=10, unique=True)
    creation_date = models.DateTimeField(auto_now_add=True)


class Post(models.Model):
    subject = models.CharField(max_length=160)
    content = models.CharField(max_length=800)
    public = models.BooleanField(default=False)
    post_date = models.DateTimeField(auto_now_add=True)
    followers = models.ManyToManyField(User, related_name='user_followers')
    author = models.ForeignKey(User, related_name='user_author', on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, related_name="tagged")

    def get_absolute_url(self):
        return reverse('show-post', kwargs={'post_id': self.id})

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('subject', 'content', 'public')

class Notification(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.CharField(max_length=36,default="New comment on a post you follow")
    notif_date = models.DateTimeField(auto_now_add=True)

comment_was_posted.connect(notify_followers)
