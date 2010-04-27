# -*- coding: utf-8 -*-
from django.utils import simplejson
from django.core.urlresolvers import reverse
from ragendja.template import render_to_response
from ragendja.dbutils import get_object, db_create
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.create_update import create_object, delete_object, \
  update_object
from pingpong.models import Player, Team, Game
from pingpong.forms import make_player_form

def freetrial(request):
  return render_to_response(request, 'pingpong/freetrial.html')

def index(request):
  if request.user.is_authenticated():
    singles_players = Player.gql("WHERE owner = :owner ORDER BY singles_ranking_points DESC, name",
                                  owner=request.user)
    doubles_players = Player.gql("WHERE owner = :owner ORDER BY doubles_ranking_points DESC, name",
                                  owner=request.user)
    return render_to_response(request, 'pingpong/main.html',
      { 'singles_players': singles_players, 'doubles_players': doubles_players })
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

@login_required
def add_score(request):
  if not request.POST:
    players = Player.gql("WHERE owner = :owner ORDER BY name",
                         owner=request.user)
    return render_to_response(request, 'pingpong/addscore.html',
      { 'players': players, })
  else:
    # TODO: Implement validation
    try:
      # Find players. Save teams. Save game.
      t1p1 = get_object(Player, request.POST['t1p1'])
      t1p2 = get_object(Player, request.POST['t1p2'])
      t2p1 = get_object(Player, request.POST['t2p1'])
      t2p2 = get_object(Player, request.POST['t2p2'])
      t1s = int(request.POST['t1s'])
      t2s = int(request.POST['t2s'])
      t1 = db_create(Team, player1=t1p1, player2=t1p2, points=t1s)
      t2 = db_create(Team, player1=t2p1, player2=t2p2, points=t2s)
      game = db_create(Game, team1=t1, team2=t2)

      # TODO: Adjust appropriate ranking points and last movement values
    
      response_dict = { 'status': True, 'message': 'Scores successfully saved.' }
    except:
      # TODO: Populate this in the case of an error
      response_dict = { 'status': False, 'message' : 'Hmmm. There was a problem saving your scores - please have another go.' }
    return HttpResponse(simplejson.dumps(response_dict), mimetype='application/json')

@login_required
def list_players(request):
  return object_list(request, Player.gql("WHERE owner = :owner ORDER BY name",
                                         owner=request.user), paginate_by=20)

@login_required
def show_player(request, key):
  return object_detail(request, Player.all(), key)

@login_required
def add_player(request):
  PlayerForm = make_player_form(request)
  return create_object(request, form_class=PlayerForm,
    post_save_redirect=reverse('pingpong.views.show_player',
                               kwargs=dict(key='%(key)s')))

@login_required
def edit_player(request, key):
  PlayerForm = make_player_form(request)
  return update_object(request, object_id=key, form_class=PlayerForm,
    post_save_redirect=reverse('pingpong.views.show_player',
                               kwargs=dict(key='%(key)s')))

@login_required
def delete_player(request, key):
  return delete_object(request, Player, object_id=key,
    post_delete_redirect=reverse('pingpong.views.list_players'))
