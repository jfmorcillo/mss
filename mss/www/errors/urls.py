from django.conf.urls import patterns, url

from mss.www.errors import views

urlpatterns = patterns('',
    url(r'^sent/$', views.user_error_submit, name="user_error_submit"),
)
