from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from secure_witness import views

urlpatterns = patterns('',
    url(r'^$', login_required(views.IndexView.as_view()), name='index'),
		url(r'^adduser/', views.lexusadduser, name='adduser')
)
