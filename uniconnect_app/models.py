from django.db import models
from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


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


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'location', 'birth_date')


class Post(models.Model):
    subject = models.CharField(max_length=160)
    content = models.CharField(max_length=800)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    public = models.BooleanField(default=False)
    post_date = models.DateTimeField(auto_now_add=True)


class Tag(models.Model):
    # We will use the implcit id
    tag = models.CharField(max_length=10, unique=True)
    creation_date = models.DateTimeField(auto_now_add=True)


class PostTag(models.Model):
    post = models.ForeignKey(Post)
    tag = models.ForeignKey(Tag)
