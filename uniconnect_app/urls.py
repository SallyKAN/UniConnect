from django.conf.urls import url


from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^me/', views.me, name='me'),
    url(r'^notifications/', views.notifications, name='notifications'),
    url(r'^submit/', views.submit_profile, name='submit_profile'),
    url(r'^post/$', views.create_post, name='create-post'),
    url(r'^post/(?P<post_id>\d+)/$', views.show_post, name='show-post'),
    url(r'^profile/(?P<username>\w+)/$', views.update_profile, name='profile'),
    url(r'^tag/(?P<tag>\w+)/$', views.tag_view, name='tag-view'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
]
