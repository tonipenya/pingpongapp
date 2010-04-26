# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('pingpong.views',
  (r'^$', 'index'),
  (r'^freetrial/$', 'freetrial'),
  (r'^login/$', 'login'),
  (r'^signup/$', 'signup'),
  (r'^score/add/$', 'add_score'),
)
