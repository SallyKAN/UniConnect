from django.shortcuts import render
from django.http import (
    HttpResponseNotAllowed, HttpResponseRedirect, HttpResponse,
    HttpResponseForbidden, HttpResponseNotFound,
)
import random
from .models import Notification, Tag, Post, User, UserForm, ProfileForm,Profile, PostForm
from .forms import TilForm, RegisterForm,SelectForm
from .tokens import account_activation_token
from datetime import datetime
from  django_comments.models import Comment
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.views.generic import DetailView, TemplateView
from .serializers import PostSerializer,UserSerializer,ProfileSerializer,CommentSerializer
from rest_framework import generics
import pytz
from django.db.models import Q
from django.shortcuts import render_to_response, get_object_or_404
from django_comments.views.moderation import perform_delete
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime, timezone
@login_required
@transaction.atomic
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, ('Your profile was successfully updated!'))
            u = request.user.username
            url = reverse('profile', kwargs={'username': u})
            return HttpResponseRedirect(url)
        else:
            messages.error(request, ('Please correct the error below.'))
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'uniconnect_app/submit.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


def profile(request, username):
    user = User.objects.get(username=username)
    posts = Post.objects.filter(author=user)
    latest_tags = Tag.objects.filter(tagged__in=posts).distinct()
    user.save()
    return render(request,'uniconnect_app/profile.html',{
        'u': user,
        'posts': posts,
        'tags': latest_tags,
    })


def index(request):
    if not request.user.is_authenticated:
        now = datetime.now(timezone.utc)
        latest_posts_all = Post.objects.filter(public=True).order_by('-post_date')
        latest_posts_paginator = Paginator(latest_posts_all, 15)
        latest_posts_page = request.GET.get('page')
        try:
            latest_posts = latest_posts_paginator.page(latest_posts_page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            latest_posts = latest_posts_paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            latest_posts = latest_posts_paginator.page(latest_posts_paginator.num_pages)
        oldest_posts_all = Post.objects.filter(public=True).order_by('post_date')
        oldest_posts_paginator = Paginator(oldest_posts_all, 15)
        oldest_posts_page = request.GET.get('page')
        try:
            oldest_posts = oldest_posts_paginator.page(oldest_posts_page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            oldest_posts = oldest_posts_paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            oldest_posts = oldest_posts_paginator.page(oldest_posts_paginator.num_pages)
        tags = Tag.objects.filter(tagged__in=latest_posts_all).distinct()
        if request.method == 'GET':
            select_form = SelectForm()
        if request.method == 'POST':
            select_form = SelectForm(request.POST)
            if select_form.is_valid():
                order = select_form.cleaned_data.get('order')
                if order == 'Oldest':
                    return render(
                    request, 'uniconnect_app/index.html', {
                             'posts':oldest_posts,
                             'tags': tags,
                             'now':now,
                            'select_form': select_form
                                })
                elif order == 'Newest':
                    return render(
                    request, 'uniconnect_app/index.html', {
                        'posts': latest_posts,
                        'tags': tags,
                            'now': now,
                        'select_form': select_form
                    })
                elif order == 'Recommended':
                    return HttpResponseRedirect('/login/')
        return render(
            request, 'uniconnect_app/index.html', {
                'posts': latest_posts,
                'tags': tags,
                'now': now,
                'select_form': select_form
            })
    else:
        return HttpResponseRedirect('/me/')


def me(request):
    if request.user.is_authenticated:
        posts = Post.objects.filter(author=request.user)
        rec_posts = []
        for post in posts:
            tags = post.tags.all()
            for tag in tags:
                p = Post.objects.filter(tags=tag)
                rec_posts.extend(p)
        now = datetime.now(timezone.utc)
        latest_posts_all = Post.objects.filter(public=True).order_by('-post_date')
        rec_posts = list(set(rec_posts))
        latest_posts_paginator = Paginator(latest_posts_all, 15)
        latest_posts_page = request.GET.get('page')
        try:
            latest_posts = latest_posts_paginator.page(latest_posts_page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            latest_posts = latest_posts_paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            latest_posts = latest_posts_paginator.page(latest_posts_paginator.num_pages)
        oldest_posts_all = Post.objects.filter(public=True).order_by('post_date')
        oldest_posts_paginator = Paginator(oldest_posts_all, 15)
        oldest_posts_page = request.GET.get('page')
        try:
            oldest_posts = oldest_posts_paginator.page(oldest_posts_page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            oldest_posts = oldest_posts_paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            oldest_posts = oldest_posts_paginator.page(oldest_posts_paginator.num_pages)
        tags = Tag.objects.filter(tagged__in=latest_posts_all).distinct()
        if request.method == 'GET':
            select_form = SelectForm()
        if request.method == 'POST':
            select_form = SelectForm(request.POST)
            if select_form.is_valid():
                order = select_form.cleaned_data.get('order')
                if order == 'Oldest':
                    return render(
                        request, 'uniconnect_app/index.html', {
                            'posts': oldest_posts,
                            'tags': tags,
                            'now': now,
                            'select_form': select_form
                        })
                elif order == 'Newest':
                    return render(
                        request, 'uniconnect_app/index.html', {
                            'posts': latest_posts,
                            'tags': tags,
                            'now': now,
                            'select_form': select_form
                        })
                elif order == 'Recommended':
                    return render(
                        request, 'uniconnect_app/index.html', {
                            'posts': rec_posts,
                            'tags': tags,
                            'now': now,
                            'select_form': select_form
                        })
        return render(
            request, 'uniconnect_app/index.html', {
                'posts': latest_posts,
                'tags': tags,
                'now': now,
                'select_form': select_form
            })
    else:
        return HttpResponseRedirect('/login/')


def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/me/')
    if request.method == 'GET':
        form = AuthenticationForm()
        return render(request, 'uniconnect_app/login.html', {'form': form})
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                print(user)
                login(request, user)
                return HttpResponseRedirect('/me/')
            else:
                print('User not found')
        else:
            # If there were errors, we render the form with these
            # errors
            return render(request, 'uniconnect_app/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


def signup(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/me/')
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'uniconnect_app/signup.html', {'form': form})
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # https://docs.djangoproject.com/en/1.11/topics/forms/modelforms/#the-save-method
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            message = render_to_string('activate_email.html', {
                'user': user,
                'domain': '127.0.0.1:8000',
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            mail_subject = 'Activate your Uniconnect account.'
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return HttpResponse('Please confirm your email address to complete the registration')
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return HttpResponseRedirect('/me/')
        else:
            return render(request, 'uniconnect_app/signup.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        return HttpResponseRedirect('/me/')
    else:
        return HttpResponse('Activation link is invalid!')


def create_post(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    elif request.method == 'GET':
        form = TilForm()
        latest_posts = Post.objects.filter(author=request.user).order_by('-post_date')[:5]
        return render(
            request, 'uniconnect_app/create_post.html', {
                'form': form, 'posts': latest_posts,
            })
    elif request.method == 'POST':
        form = TilForm(request.POST)
        if form.is_valid():
            p = Post(
                subject=form.cleaned_data.get('subject'),
                picture_link=form.cleaned_data.get('picture_link'),
                content=form.cleaned_data.get('content'),
                author=request.user,
                public=form.cleaned_data.get('public'),
            )
            p.save()
            p.followers.add(request.user)
            tags = form.cleaned_data.get('tags')
            if tags:
                tags_list = tags.split(',')
                for tag in tags_list:
                    tag = tag.strip()
                    t = Tag.objects.filter(tag=tag)
                    if not t:
                        t = Tag(tag=tag)
                        t.save()
                    else:
                        t = t[0]
                    p.tags.add(t)

            return HttpResponseRedirect('/post/{0}/'.format(p.id))
        else:
            return render(
                request, 'uniconnect_app/create_post.html', {
                    'form': form,
                })
    else:
        return HttpResponseNotAllowed('{0} Not allowed'.format(request.method))

def edit_post(request, post_id):
    post = Post.objects.get(pk=post_id)
    if request.method == 'POST':
        post_form = PostForm(request.POST, instance=post)
        if post_form.is_valid():
            post_form.save()
            messages.success(request, ('Your post has been successfully updated!'))
            u = post_id
            url = reverse('show-post', kwargs={'post_id': u})
            return HttpResponseRedirect(url)
        else:
            messages.error(request, ('Please correct the error below.'))
    else:
        post_form = PostForm(instance=post)
    return render(request, 'uniconnect_app/editposts.html', {
        'form': post_form,
    })


def delete_post(request,post_id=None):
    post = get_object_or_404(Post, pk=post_id)
    post.delete()
    return redirect('/')


def follow_post(request, post_id=None):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    post = get_object_or_404(Post, pk=post_id)
    if request.user in post.followers.all():
        post.followers.remove(request.user)
        data = {'following': False}
        print(str(request.user.id) + " no longer following " + str(post.id))
    else:
        post.followers.add(request.user)
        data = {'following': True}
        print(str(request.user.id) + " following " + str(post.id))
    post.save()
    return JsonResponse(data)


def delete_own_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.user.id != request.user.id:
        raise Http404
    perform_delete(request, comment)
    return HttpResponseRedirect(comment.content_object.get_absolute_url())
    comment.save()
def comment_posted( request ):
    if request.GET['c']:
        comment_id, post_id = request.GET['c'].split(':')
        post = Post.objects.get(pk=post_id)
        if post:
            return HttpResponseRedirect(post.get_absolute_url())
    return HttpResponseRedirect("/")

def show_post(request, post_id=None):
    post = Post.objects.filter(id=post_id)[0]
    # if the post is not public, only viewable by the author
    if not post.public:
        if not post.author == request.user:
            return HttpResponseForbidden()
    post_tags = post.tags.all()
    return render(request, 'uniconnect_app/view_post.html', {
        'post': post,
        'tags': post_tags if len(post_tags) else None,
    })


def search(request):
    if request.method == 'GET':
        search_query = request.GET.get('q')
        search_posts = Post.objects.filter(Q(subject__icontains=search_query ) | Q(content__icontains=search_query )
                                           |Q(author__username__icontains=search_query) |Q(tags__tag__icontains=search_query))

        return render(
            request, 'uniconnect_app/search.html',{
             'search_posts': search_posts,
             'search_query': search_query,
            })

def tag_view(request, tag):
    t = Tag.objects.filter(tag=tag)
    if t.all():
        t = t[0]
        posts = t.tagged.all()
        # Query all the public posts or the posts by
        # the currently logged in user with the
        # given tag
        posts = Post.objects.filter(id__in=[
            p.id for p in posts if p.public or
            p.author == request.user]
        )
        return render(request, 'uniconnect_app/tag_view.html', {
            'tag': t.tag,
            'posts': posts,
        })
    else:
        return HttpResponseNotFound('<h1> Tag Not Found </h1>')


def notifications(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    notifis = Notification.objects.filter(
            owner=request.user
    )
    tz=pytz.timezone('Australia/Sydney')
    return render(
        request, 'uniconnect_app/notifications.html', {
            'notifications': notifis,
            'current_time': datetime.now(tz=tz)
        })




def delete_notification(request, notif_id=None):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    notification = Notification.objects.get(id=notif_id)
    if notification.owner == request.user:
        notification.delete()
    return redirect('/notifications/')



# REST api view.
class PostCreateView(generics.ListCreateAPIView):
    """This class defines the create behavior of our rest api."""
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        content = {
            'user': str(request.user),  # `django.contrib.auth.User` instance.
            'auth': str(request.auth),  # None
        }
        return Response(content)

    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        """Save the post data when creating a new bucketlist."""
        serializer.save()


class PostDetailsView(generics.RetrieveUpdateDestroyAPIView):
    """This class handles the http GET, PUT and DELETE requests."""
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class UserCreateView(generics.ListCreateAPIView):
    """This class defines the create behavior of our rest api."""
    """Allows access only to admin users."""
    permission_classes = (IsAdminUser,)

    def has_permission(self, request, view):
        return request.user and request.user.is_staff

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        """Save the post data when creating a new bucketlist."""
        serializer.save()


class UserDetailsView(generics.RetrieveUpdateDestroyAPIView):
    """This class handles the http GET, PUT and DELETE requests."""


    queryset = User.objects.all()
    serializer_class = UserSerializer


class ProfileCreateView(generics.ListCreateAPIView):
    """This class defines the create behavior of our rest api."""
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        content = {
            'user': str(request.user),  # `django.contrib.auth.User` instance.
            'auth': str(request.auth),  # None
        }
        return Response(content)

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def perform_create(self, serializer):
        """Save the post data when creating a new bucketlist."""
        serializer.save()


class ProfileDetailsView(generics.RetrieveUpdateDestroyAPIView):


    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class CommentCreateView(generics.ListCreateAPIView):
    """This class defines the create behavior of our rest api."""
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        content = {
            'user': str(request.user),  # `django.contrib.auth.User` instance.
            'auth': str(request.auth),  # None
        }
        return Response(content)

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        """Save the post data when creating a new bucketlist."""
        serializer.save()


class CommentDetailsView(generics.RetrieveUpdateDestroyAPIView):
    

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer