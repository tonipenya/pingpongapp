# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('pingpong.views',
  (r'^$', 'index'),
  (r'^freetrial/$', 'freetrial'),
  (r'^login/$', 'login'),
  (r'^settings/$', 'settings'),
  (r'^signup/$', 'signup'),
  (r'^score/add/$', 'add_score'),
  (r'^players/$', 'list_players'),
  (r'^player/add/$', 'add_player'),
  (r'^player/(?P<key>.+)$', 'show_player'),
  (r'^player/edit/(?P<key>.+)$', 'edit_player'),
  (r'^player/delete/(?P<key>.+)$', 'delete_player'),
)
