# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('pingpong.views',
  (r'^$', 'index'),
  (r'^login_popup$', 'login_popup'),
)
