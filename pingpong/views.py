# -*- coding: utf-8 -*-
from ragendja.template import render_to_response

def index(request):

  # TODO: Decide whether we should show the marketing page (index.html), or the app home page (main.html)

  return render_to_response(request, 'pingpong/index.html')

def login_popup(request):
  return render_to_response(request, 'pingpong/login_popup.html')
