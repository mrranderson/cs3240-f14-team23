from django.conf.urls import patterns, include, url
from django.contrib import admin
from secure_witness import views
from django.conf import settings
from django.conf.urls.static import static

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
        url(r'^detail_user/(?P<bulletin_id>\d+)/', views.detail_user, name='detail_user'),
        url(r'^accept_notification/(?P<notification_id>\d+)/', views.accept_notification, name='accept_notification'),
        url(r'^reject_notification/(?P<notification_id>\d+)/', views.reject_notification, name='reject_notification'),
        url(r'^delete_notification/(?P<notification_id>\d+)/', views.delete_notification, name='delete_notification'),
        url(r'^create_folder/', views.create_folder, name='create_folder'),
        url(r'^create_private_folder/', views.create_private_folder, name='create_private_folder'),
        url(r'^detail_folder/(?P<folder_id>\d+)/', views.detail_folder, name='detail_folder'),
        url(r'^delete_folder/(?P<folder_id>\d+)/', views.delete_folder, name='delete_folder'),
        url(r'^edit_folder/(?P<folder_id>\d+)/', views.edit_folder, name='edit_folder'),
        url(r'^manage', views.manage_user, name='manage'),
        url(r'^delete', views.delete_user, name='delete'),
        url(r'^all_global_folders/', views.all_global_folders, name='all_global_folders'),
        url(r'^all_private_folders/', views.all_private_folders, name='all_private_folders'),
        url(r'^all_my_bulletins/', views.all_my_bulletins, name='all_my_bulletins'),
        url(r'^all_followed_bulletins/', views.all_followed_bulletins, name='all_followed_bulletins'),
        url(r'^all_public_bulletins/', views.all_public_bulletins, name='all_public_bulletins'),
        url(r'^copy_bulletin/(?P<bulletin_id>\d+)/', views.copy_bulletin, name='copy_bulletin'),
        url(r'^decrypt_document/(?P<bulletin_id>\d+)/', views.decrypt_document, name='decrypt_document'),
        url(r'^encrypt_document/(?P<bulletin_id>\d+)/', views.encrypt_document, name='encrypt_document'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
