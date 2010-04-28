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

    # TODO: Validation!

    try:
      # Find players. Save teams. Save game.
      t1p1 = get_object(Player, request.POST['t1p1'])
      t1p2 = get_object(Player, request.POST['t1p2'])
      t2p1 = get_object(Player, request.POST['t2p1'])
      t2p2 = get_object(Player, request.POST['t2p2'])
      t1s = float(request.POST['t1s'])
      t2s = float(request.POST['t2s'])
      t1 = db_create(Team, player1=t1p1, player2=t1p2, points=t1s)
      t2 = db_create(Team, player1=t2p1, player2=t2p2, points=t2s)
      game = db_create(Game, team1=t1, team2=t2)

      # TODO: Split this all up once it's been ported and tested

      doubles = (t1p1 != None and t1p2 != None and t2p1 != None and t2p2 != None)
      team1_ranking_points = 0
      team2_ranking_points = 0
      if doubles:
        reset_doubles_last_movements(request.user)
        team1_ranking_points = (t1p1.doubles_ranking_points + t1p2.doubles_ranking_points) / 2
        team2_ranking_points = (t2p1.doubles_ranking_points + t2p2.doubles_ranking_points) / 2
      else:
        reset_singles_last_movements(request.user)
        team1_ranking_points = t1p1.singles_ranking_points
        team2_ranking_points = t2p1.singles_ranking_points
      game_ranking_points = (team1_ranking_points + team2_ranking_points) / 2

      # Each team scores points equal to game rating +- winning margin * 100 / max score
      team1_points = game_ranking_points + (t1s - t2s) * 100 / max(t1s, t2s)
      team2_points = game_ranking_points + (t2s - t1s) * 100 / max(t1s, t2s)

      # Save ranking points for game - if team 1 won, p1 (and p3) are winning team, otherwise
      # p2 (and p4) are the winning team
      if doubles:
        game.p1_ranking_points = team1_points + (t1p1.doubles_ranking_points - t1p2.doubles_ranking_points) / 2
        game.p2_ranking_points = team2_points + (t2p1.doubles_ranking_points - t2p2.doubles_ranking_points) / 2
        game.p3_ranking_points = 2 * team1_points - game.p1_ranking_points
        game.p4_ranking_points = 2 * team2_points - game.p2_ranking_points
      else:
        game.p1_ranking_points = team1_points
        game.p2_ranking_points = team2_points
      game.put()

      # Update player ranking points
      decay_factor = 10
      if doubles:
        old_t1p1_ranking_points = t1p1.doubles_ranking_points
        old_t2p1_ranking_points = t2p1.doubles_ranking_points
        t1p1.doubles_ranking_points = t1p1.doubles_ranking_points / decay_factor * (decay_factor - 1) + game.p1_ranking_points / decay_factor
        t2p1.doubles_ranking_points = t2p1.doubles_ranking_points / decay_factor * (decay_factor - 1) + game.p2_ranking_points / decay_factor
        t1p1.doubles_last_movement = t1p1.doubles_ranking_points - old_t1p1_ranking_points
        t2p1.doubles_last_movement = t2p1.doubles_ranking_points - old_t2p1_ranking_points
        t1p1.put()
        t2p1.put()

        old_t1p2_ranking_points = t1p2.doubles_ranking_points
        old_t2p2_ranking_points = t2p2.doubles_ranking_points
        t1p2.doubles_ranking_points = t1p2.doubles_ranking_points / decay_factor * (decay_factor - 1) + game.p3_ranking_points / decay_factor
        t2p2.doubles_ranking_points = t2p2.doubles_ranking_points / decay_factor * (decay_factor - 1) + game.p4_ranking_points / decay_factor
        t1p2.doubles_last_movement = t1p2.doubles_ranking_points - old_t1p2_ranking_points
        t2p2.doubles_last_movement = t2p2.doubles_ranking_points - old_t2p2_ranking_points
        t1p2.put()
        t2p2.put()
      else:
        old_t1p1_ranking_points = t1p1.singles_ranking_points
        old_t2p1_ranking_points = t2p1.singles_ranking_points
        t1p1.singles_ranking_points = t1p1.singles_ranking_points / decay_factor * (decay_factor - 1) + game.p1_ranking_points / decay_factor
        t2p1.singles_ranking_points = t2p1.singles_ranking_points / decay_factor * (decay_factor - 1) + game.p2_ranking_points / decay_factor
        t1p1.singles_last_movement = t1p1.singles_ranking_points - old_t1p1_ranking_points
        t2p1.singles_last_movement = t2p1.singles_ranking_points - old_t2p1_ranking_points
        t1p1.put()
        t2p1.put()
      response_dict = { 'status': True, 'message': 'Scores successfully saved.' }
    except:
      response_dict = { 'status': False, 'message' : 'Hmmm. There was a problem saving your scores - please have another go.' }
    return HttpResponse(simplejson.dumps(response_dict), mimetype='application/json')

def reset_singles_last_movements(user):
  players = Player.gql("WHERE owner = :owner", owner=user)
  for p in players:
    p.singles_last_movement = 0.0
    p.put()

def reset_doubles_last_movements(user):
  players = Player.gql("WHERE owner = :owner", owner=user)
  for p in players:
    p.doubles_last_movement = 0.0
    p.put()

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
