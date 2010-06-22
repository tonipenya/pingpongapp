 # -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('pingpong.views',
  (r'^$', 'index'),
  (r'^home/$', 'home'),
  (r'^login/$', 'login'),
  (r'^settings/$', 'settings'),
  (r'^upgrade/$', 'upgrade'),
  (r'^paypal/$', 'paypal'),
  (r'^ipn/$', include('paypal.standard.ipn.urls')),
  (r'^terms/$', 'terms'),
  (r'^privacy/$', 'privacy'),
  (r'^contact/$', 'contact'),
  (r'^thanks/$', 'thanks'),
  (r'^about/$', 'about'),
  (r'^score/add/$', 'add_score'),
  (r'^players/$', 'list_players'),
  (r'^player/add/$', 'add_player'),
  (r'^player/stats/(?P<key>.+)$', 'player_stats'),
  (r'^player/edit/(?P<key>.+)$', 'edit_player'),
  (r'^player/delete/(?P<key>.+)$', 'delete_player'),
  (r'^player/(?P<key>.+)$', 'show_player'),
)
