# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from ragendja.urlsauto import urlpatterns
from ragendja.auth.urls import urlpatterns as auth_patterns
from django.contrib import admin
from pingpong.forms import UserRegistrationForm

admin.autodiscover()

handler500 = 'ragendja.views.server_error'

urlpatterns += auth_patterns + patterns('',
  ('^admin/(.*)', admin.site.root),
  url(r'^register/$', 'registration.views.register',
      kwargs={'form_class': UserRegistrationForm},
      name='registration_register'),
)
