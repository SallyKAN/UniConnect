from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^me/', views.me, name='me'),
    url(r'^notifications/$', views.notifications, name='notifications'),
    url(r'^notifications/(?P<notif_id>\d+)/delete/$', views.delete_notification, name='delete_notification'),
    url(r'^submit/', views.submit_profile, name='submit_profile'),
    url(r'^post/$', views.create_post, name='create-post'),
    url(r'^post/(?P<post_id>\d+)/edit/$', views.update_post, name='update-post'),
    url(r'^post/(?P<post_id>\d+)/delete/$', views.delete_post, name='delete-post'),
    url(r'^post/(?P<post_id>\d+)/follow/$',views.follow_post,name='follow-post'),
    url(r'^post/(?P<post_id>\d+)/unfollow/$',views.unfollow_post,name='unfollow-post'),
    url(r'^comments/posted/$', views.comment_posted),
    url(r'^comments/delete_own/(?P<comment_id>.*)/$', views.delete_own_comment, name='delete_own_comment'),
    url(r'^post/(?P<post_id>\d+)/$', views.show_post, name='show-post'),
    url(r'^profile/(?P<username>\w+)/$', views.update_profile, name='profile'),
    url(r'^tag/(?P<tag>\w+)/$', views.tag_view, name='tag-view'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    url(r'^post/search$', views.search, name='search-view'),
    url(r'^postapi/$', views.PostCreateView.as_view(), name="create"),
    url(r'^postapi/(?P<pk>[0-9]+)/$', views.PostDetailsView.as_view(), name="details"),
    url(r'^userapi/$', views.UserCreateView.as_view(), name="create"),
    url(r'^userapi/(?P<pk>[0-9]+)/$', views.UserDetailsView.as_view(), name="details"),
    url(r'^profileapi/$', views.ProfileCreateView.as_view(), name="create"),
    url(r'^profileapi/(?P<pk>[0-9]+)/$', views.ProfileDetailsView.as_view(), name="details"),
    url(r'^commentapi/$', views.CommentCreateView.as_view(), name="create"),
    url(r'^profileapi/(?P<pk>[0-9]+)/$', views.CommentDetailsView.as_view(), name="details"),
    url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete')
]
