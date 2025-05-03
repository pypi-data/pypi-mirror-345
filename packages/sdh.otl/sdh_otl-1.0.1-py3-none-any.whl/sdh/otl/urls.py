from django.urls import re_path

from . import views


urlpatterns = [
    re_path(r'^(?P<otp_key>\w+)/$', views.otl_view, name='one-time-link'),
]
