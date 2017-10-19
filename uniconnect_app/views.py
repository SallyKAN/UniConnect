from django.shortcuts import render
from django.http import (
    HttpResponseNotAllowed, HttpResponseRedirect, HttpResponse,
    HttpResponseForbidden, HttpResponseNotFound,
)
from .models import Post, Tag, PostTag, User, UserForm, ProfileForm
from .forms import TilForm, RegisterForm
from .tokens import account_activation_token

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


@login_required
@transaction.atomic
def submit_profile(request):
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


def update_profile(request, username):
    user = User.objects.get(username=username)
    user.profile.bio = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit...'
    user.save()
    return render(request,'uniconnect_app/profile.html')


def index(request):
    if not request.user.is_authenticated:
        latest_posts = Post.objects.filter(public=True).order_by('-post_date')[:5]
        return render(
            request, 'uniconnect_app/index.html', {
                'posts': latest_posts
            })
    else:
        return HttpResponseRedirect('/me/')


def me(request):
    if request.user.is_authenticated:
        latest_posts = Post.objects.order_by('-post_date')
        post_tags = PostTag.objects.filter(
            post__in=[p for p in latest_posts]
        ).distinct()
        return render(
            request, 'uniconnect_app/me.html', {
                'user': request.user,
                'posts': latest_posts,
                'tags': set([tag.tag for tag in post_tags]),
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
                'domain': 'http://127.0.0.1:8000',
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
            # If there were errors, we render the form with these
            # errors
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
                'form': form, 'posts': latest_posts
            })
    elif request.method == 'POST':
        form = TilForm(request.POST)
        if form.is_valid():
            p = Post(
                subject=form.cleaned_data.get('subject'),
                content=form.cleaned_data.get('content'),
                author=request.user,
                public=form.cleaned_data.get('public'),
            )
            p.save()
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
                    pt = PostTag(post=p, tag=t)
                    pt.save()

            return HttpResponseRedirect('/post/{0}/'.format(p.id))
        else:
            return render(
                request, 'uniconnect_app/create_post.html', {
                    'form': form,
                })
    else:
        return HttpResponseNotAllowed('{0} Not allowed'.format(request.method))


def show_post(request, post_id=None):
    post = Post.objects.filter(id=post_id)[0]
    # if the post is not public, only viewable by the author
    if not post.public:
        if not post.author == request.user:
            return HttpResponseForbidden()
    post_tags = PostTag.objects.filter(post=post)
    return render(request, 'uniconnect_app/view_post.html', {
        'post': post,
        'tags': post_tags if len(post_tags) else None,
    })


def tag_view(request, tag):
    t = Tag.objects.filter(tag=tag)
    if t.all():
        t = t[0]
        posts = PostTag.objects.filter(tag=t)
        # Query all the public posts or the posts by
        # the currently logged in user with the
        # given tag
        posts = Post.objects.filter(id__in=[
            p.post.id for p in posts if p.post.public or
            p.post.author == request.user]
        )
        return render(request, 'uniconnect_app/tag_view.html', {
            'tag': t.tag,
            'posts': posts,
        })
    else:
        return HttpResponseNotFound('<h1> Tag Not Found </h1>')
