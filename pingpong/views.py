# -*- coding: utf-8 -*-
from ragendja.template import render_to_response

def index(request):
  if request.user.is_authenticated():
    return render_to_response(request, 'pingpong/main.html')
  else:
    return render_to_response(request, 'pingpong/index.html')

def login_popup(request):
  return render_to_response(request, 'pingpong/login_popup.html')
