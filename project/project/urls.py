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
)
