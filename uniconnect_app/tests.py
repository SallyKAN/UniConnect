from django.test import TestCase, SimpleTestCase
from django.test import Client
from django.urls import reverse
from .models import Notification, User, Post, Profile, Tag
from django.contrib.auth.models import User
from uniconnect_app.views import create_post
from django.test.utils import setup_test_environment
from django.template.response import SimpleTemplateResponse, TemplateResponse
from .forms import *
from django.utils import timezone
from django.core import mail
from django_comments.forms import CommentForm
from django_comments.models import Comment
# Create your tests here.

def create_notif(user, post):
    return Notification.objects.create(owner=user, post=post, notif_date= timezone.now())

def create_user(email, first_name, last_name, password, u):
    return User.objects.create(first_name=first_name, last_name=last_name, email=email, password=password, username=u)

def create_post(s,c,p,f,a, t):
    return Post.objects.create(subject=s, content=c, public=p, post_date=timezone.now(), followers=f, author=a, id=1, tags = t)

class Notif_Follow_Tests(TestCase):

    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'secret'}
        User.objects.create_user(**self.credentials)

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('notifications'))
        self.assertRedirects(resp, '/login/')

    def test_author_notif(self):
        t = []
        user = create_user("eve", "lee", "eve@example.com", "Password123", "eve")
        u = []
        u.append(user)
        p = create_post("test", "testing", True, u, user, t)
        n = create_notif(user, p)
        noti = []
        noti.append(n)
        l = list(Notification.objects.filter(owner=user))
        self.assertEqual(noti, l)

    def test_followers(self):
        t = []
        user_a = create_user("eve", "lee", "eve@example.com", "Password123", "eve")
        user_b = create_user("evelyn", "lee", "evelyn@example.com", "Password123", "evelyn")
        u = []
        u.append(user_a)
        u.append(user_b)
        p = create_post("test", "testing", True, u, user_a, t)
        posts = Post.objects.filter(author=user_a)
        fol =  []
        for post in posts:
            l = list(post.followers.all())
            fol.extend(l)
        self.assertEqual(u, fol)

class PassReset(TestCase):

    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'secret'}

    def test_rest_pass(self):
        User.objects.create_user(**self.credentials)
        response = self.client.post(reverse('password_reset'),
                                    data={'email':'test@example.com'})
        self.assertEqual(len(mail.outbox), 1)

    def test_rest_pass_fail_non_user(self):
        response = self.client.post(reverse('password_reset'),
                                    data={'email':'test@example.com'})
        self.assertEqual(len(mail.outbox), 0)

    def test_pass_reset_view_get(self):
            response = self.client.get(reverse('password_reset'))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response,
                                    'registration/password_reset_form.html')

class SignUp_Test(TestCase):

    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'secret'}

    def test_registration_view_get(self):
            response = self.client.get(reverse('signup'))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response,
                                    'uniconnect_app/signup.html')

    def test_registration_view_post_success(self):
        response = self.client.post(reverse('signup'),
                                    data={'username': 'eve',
                                          'email': 'eve@example.com',
                                          'password1': 'Password123',
                                          'password2': 'Password123'})
        self.assertEqual(len(mail.outbox), 1)

    def test_signup_fail_diff_pass(self):
        response = self.client.post(reverse('signup'),
                                    data={'username': 'eve',
                                          'email': 'eve@example.com',
                                          'password1': 'Password123',
                                          'password2': 'Password124'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', field='password2',
                             errors="The two password fields didn't match.")
        self.failIf(response.context['form'].is_valid())
        self.assertEqual(len(mail.outbox), 0)

    def test_signup_fail_too_common_pass(self):
        response = self.client.post(reverse('signup'),
                                    data={'username': 'eve',
                                          'email': 'eve@example.com',
                                          'password1': 'password',
                                          'password2': 'password'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', field='password2',
                             errors="This password is too common.")
        self.failIf(response.context['form'].is_valid())
        self.assertEqual(len(mail.outbox), 0)

    def test_signup_fail_all_numeric_pass(self):
        response = self.client.post(reverse('signup'),
                                    data={'username': 'eve',
                                          'email': 'eve@example.com',
                                          'password1': '19971996',
                                          'password2': '19971996'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', field='password2',
                             errors="This password is entirely numeric.")
        self.failIf(response.context['form'].is_valid())
        self.assertEqual(len(mail.outbox), 0)

    def test_signup_fail_pass_too_short(self):
        response = self.client.post(reverse('signup'),
                                    data={'username': 'test',
                                          'email': 'eve@example.com',
                                          'password1': 'user',
                                          'password2': 'user'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', field='password2',
                             errors="This password is too short. It must contain at least 8 characters.")
        self.failIf(response.context['form'].is_valid())
        self.assertEqual(len(mail.outbox), 0)

    def test_signup_fail_invalid_username(self):
        response = self.client.post(reverse('signup'),
                                    data={'username': '()',
                                          'email': 'eve@example.com',
                                          'password1': 'Password123',
                                          'password2': 'Password123'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', field='username',
                             errors="Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters.")
        self.failIf(response.context['form'].is_valid())
        self.assertEqual(len(mail.outbox), 0)

    def test_signup_fail_email_taken(self):
        User.objects.create_user(**self.credentials)
        response = self.client.post(reverse('signup'),
                                    data={'username': 'eve',
                                          'email': 'test@example.com',
                                          'password1': 'Password123',
                                          'password2': 'Password123'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', field='email',
                             errors="A user with that email already exists.")
        self.failIf(response.context['form'].is_valid())
        self.assertEqual(len(mail.outbox), 0)

    def test_signup_fail_username_as_pass(self):
        response = self.client.post(reverse('signup'),
                                    data={'username': 'evelynlee',
                                          'email': 'eve@example.com',
                                          'password1': 'evelynlee',
                                          'password2': 'evelynlee'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', field='password2',
                             errors="The password is too similar to the username.")
        self.failIf(response.context['form'].is_valid())
        self.assertEqual(len(mail.outbox), 0)

    def test_signup_fail_username_taken(self):
        User.objects.create_user(**self.credentials)
        response = self.client.post(reverse('signup'),
                                    data={'username': 'testuser',
                                          'email': 'eve@example.com',
                                          'password1': 'Password123',
                                          'password2': 'Password123'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', field='username',
                             errors="A user with that username already exists.")
        self.failIf(response.context['form'].is_valid())
        self.assertEqual(len(mail.outbox), 0)

    def test_registration_profile_created(self):
        User.objects.create_user(**self.credentials)
        self.assertEqual(Profile.objects.count(), 1)

class LogIn(TestCase):
    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'secret'}

    def test_login_view_get(self):
            response = self.client.get(reverse('login'))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response,
                                    'uniconnect_app/login.html')

    def test_signin_fail_wrong_pass(self):
        User.objects.create_user(**self.credentials)
        response = self.client.post(reverse('login'),
                                    data={'username': 'testuser',
                                          'password': 'secrets'})
        self.assertEqual(response.status_code, 200)
        self.failIf(response.context['form'].is_valid())

    def test_signin_fail_wrong_username(self):
        User.objects.create_user(**self.credentials)
        response = self.client.post(reverse('login'),
                                    data={'username': 'testusers',
                                          'password': 'secret'})
        self.assertEqual(response.status_code, 200)
        self.failIf(response.context['form'].is_valid())

    def test_login(self):
        # send login data
        User.objects.create_user(**self.credentials)
        response = self.client.post('/login/', self.credentials, follow=True)
        # should be logged in now
        self.assertTrue(response.context['user'].is_active)
        self.assertRedirects(response, '/me/')

class Create_PostTestCase(TestCase):


    def test_filter(self):
        u = User.objects.create_user(username='Alpha', password='password123', email="alpha@alpha.com")
        u.save()

        self.client = Client()
        self.client.login(username='Alpha', password='password123')
        p = Post.objects.create(id=1, subject="Hello", content="Lorum Ipsom djsjdj", public=True, author=User(id=2))
        p.save()
        q = Post.objects.create(id=2, subject="Hello", content="Lorum Ipsom djsjdj", public=True, author=User(id=2))
        q.save()
        r = Post.objects.create(id=3, subject="Hello", content="Lorum Ipsom djsjdj", public=True, author=User(id=2))
        r.save()
        response = self.client.post(reverse('me'))
        self.assertEqual(response.status_code, 200)
        test_date = [r, q, p]
        comp1 = []
        for t in test_date:
            comp1.append(t.id)
        form = SelectForm(data={"order": "Oldest"})
        self.assertTrue(form.is_valid())

        posts = response.context['posts']
        ob = posts.object_list
        comp2 = []
        for o in ob:
            comp2.append(o.id)

        self.assertEquals(comp1, comp1)

    def test_create_post(self):
        u = User.objects.create_user(username='Alpha', password='password123', email="alpha@alpha.com")
        u.save()
        self.client = Client()
        self.client.login(username='Alpha', password='password123')
        p = Post.objects.create(id=2, subject="Hello", content="Lorum Ipsom djsjdj", public=True, author=User(id=1))
        p.save()
        response = self.client.get(reverse('create-post'))
        self.assertEqual(response.status_code, 200)
        response = Post.objects.get(id=2)
        self.assertEqual(response.id, 2)
        self.assertEqual(response.subject, "Hello")

    def test_create_post_nologin(self):
        response = self.client.get(reverse('create-post'))
        expectedurl = '/login/'
        self.assertEqual(response.status_code, 302)
        self.assertRedirects (response,expected_url=expectedurl)

    def test_post_view(self):
        u = User.objects.create_user(username='Alpha', password='password123', email="alpha@alpha.com")
        u.save()
        self.client = Client()
        self.client.login(username='Alpha', password='password123')
        p = Post.objects.create(id=5, subject="Hello", content="Lorum Ipsom djsjdj", public=True, author=User(id=3))
        p.save()
        response = self.client.get(reverse('show-post', kwargs={'post_id': 5}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,'Lorum Ipsom djsjdj')
        self.assertContains(response, 'Hello')
