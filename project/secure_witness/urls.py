from django.conf.urls import patterns, url

from secure_witness import views

urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='index'),
)
