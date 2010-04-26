# -*- coding: utf-8 -*-
from ragendja.template import render_to_response
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.models import User

def freetrial(request):
  return render_to_response(request, 'pingpong/freetrial.html')

def index(request):
  if request.user.is_authenticated():
    return render_to_response(request, 'pingpong/main.html')
  else:
    return render_to_response(request, 'pingpong/index.html')

def login(request):
  if request.method == 'POST':
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if user is not None:
      if user.is_active:
        auth_login(request, user)
        return HttpResponseRedirect('/')
    return render_to_response(request, 'pingpong/index.html',
      { 'login_error': 'Your username or password was invalid',
        'previous_username': request.POST['username'] })
  else:
    return HttpResponseRedirect('/')
	
def settings(request):
  return render_to_response(request, 'pingpong/settings.html')

def signup(request):
  return render_to_response(request, 'pingpong/signup.html')

def add_score(request):
  return render_to_response(request, 'pingpong/addscore.html')
