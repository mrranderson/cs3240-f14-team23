from django.conf.urls import patterns, include, url
from django.contrib import admin
from secure_witness import views
urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
		url(r'^$', include('secure_witness.urls')),
    url(r'^admin/', include(admin.site.urls)),
		url(r'^accounts/login/', 'django.contrib.auth.views.login', {'template_name': 'secure_witness/login.html'}),
		url(r'^adduser/', views.lexusadduser, name='adduser'),
        url(r'^search/', views.basic_search, name='search'),
        url(r'^logout', views.logout_user, name='logout'),
        url(r'^create_bulletin/', views.create_bulletin, name='create_bulletin'),
        url(r'^(?P<bulletin_id>\d+)/', views.detail_bulletin, name='detail_bulletin'),
        url(r'^inbox/', views.inbox, name='inbox'),
        url(r'^follow/(?P<bulletin_id>\d+)/', views.follow_bulletin, name='follow_bulletin'),
        url(r'^edit_bulletin/(?P<bulletin_id>\d+)/', views.edit_bulletin, name='edit_bulletin'),
        url(r'^request/(?P<bulletin_id>\d+)/', views.request_bulletin, name='request_bulletin'),
        url(r'^notification/(?P<notification_id>\d+)/', views.view_notification, name='view_notification'),
        url(r'^delete_bulletin/(?P<bulletin_id>\d+)/', views.delete_bulletin, name='delete_bulletin'),
)
