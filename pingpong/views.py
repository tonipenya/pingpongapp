# -*- coding: utf-8 -*-
import logging
from django.utils import simplejson
from django.forms.fields import email_re
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
from pingpong.rankings import DefaultRankingSystem

def freetrial(request):
  return render_to_response(request, 'pingpong/freetrial.html')

def index(request):
  if request.user.is_authenticated():
    singles_players = Player.gql("WHERE owner = :owner AND active = True ORDER BY singles_ranking_points DESC, name",
                                  owner=request.user)
    doubles_players = Player.gql("WHERE owner = :owner AND active = True ORDER BY doubles_ranking_points DESC, name",
                                  owner=request.user)
    return render_to_response(request, 'pingpong/main.html',
      { 'singles_players': singles_players, 'doubles_players': doubles_players })
  else:
    return render_to_response(request, 'pingpong/index.html')

def home(request):
  if request.user.is_authenticated():
    return render_to_response(request, 'pingpong/index.html')
  else:
    return HttpResponseRedirect('/')

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

@login_required
def settings(request):
  if request.method != 'POST':
    players = Player.gql("WHERE owner = :owner AND active = True ORDER BY name", owner=request.user)
    return render_to_response(request, 'pingpong/settings.html',
      { 'players': players, 'email': request.user.email })
  else:
    errors = {}
    try:
      # Save email address
      email = request.POST['email']
      if is_valid_email(email.strip()):
        user = request.user
        user.email = email.strip()
        user.save()
      else:
        errors['email'] = 'Invalid email address'
        response_dict = { 'status': False, 'message': 'Hmmm... There was a problem saving your settings - please have another go.',
          'errors': errors }
        return HttpResponse(simplejson.dumps(response_dict), mimetype='application/json')

      # Add any new players
      new_players = request.POST['newplayers']
      if new_players:
        players = new_players.splitlines()
        for p in players:
          if len(p.strip()) > 0:
            db_create(Player, name=p.strip(), owner=request.user)

      # Update player names based on posted values
      for k, v in request.POST.items():
        if str(k).endswith('_player'): # Expected key format: <key>_player
          player = get_object(Player, str(k)[:-7])
          player.name = v # Value is the updated player name
          player.put()
    
      response_dict = { 'status': True, 'message': 'Settings successfully saved.' }
    except:
      logging.exception('There was a problem saving settings')
      response_dict = { 'status': False, 'message': 'Hmmm... There was a problem saving your settings - please have another go.',
        'errors': errors }
    return HttpResponse(simplejson.dumps(response_dict), mimetype='application/json')

def is_valid_email(email):
    return True if email_re.match(email) else False

def signup(request):
  return render_to_response(request, 'pingpong/signup.html')

@login_required
def add_score(request):
  if request.method != 'POST':
    players = Player.gql("WHERE owner = :owner AND active = True ORDER BY name", owner=request.user)
    return render_to_response(request, 'pingpong/addscore.html',
      { 'players': players, })
  else:
    mode = 'singles' # Used when we re-direct back to the main view
    try:
      # Find players. Save teams. Save game using a ranking system.
      t1p1 = get_object(Player, request.POST['t1p1'])
      t1p2 = get_object(Player, request.POST['t1p2'])
      t2p1 = get_object(Player, request.POST['t2p1'])
      t2p2 = get_object(Player, request.POST['t2p2'])
      t1s = float(request.POST['t1s'])
      t2s = float(request.POST['t2s'])
      t1 = db_create(Team, player1=t1p1, player2=t1p2, points=t1s)
      t2 = db_create(Team, player1=t2p1, player2=t2p2, points=t2s)
      game = db_create(Game, team1=t1, team2=t2)
      doubles = (t1p1 != None and t1p2 != None and t2p1 != None and t2p2 != None)
      if doubles:
        mode = 'doubles'
      ranking_system = DefaultRankingSystem()
      ranking_system.save_game(t1p1=t1p1, t1p2=t1p2, t2p1=t2p1, t2p2=t2p2, 
        t1s=t1s, t2s=t2s, t1=t1, t2=t2, game=game, doubles=doubles)
      response_dict = { 'status': True, 'message': 'Scores successfully saved.', 'mode': mode }
    except:
      logging.exception('There was a problem adding scores')
      response_dict = { 'status': False, 'message' : 'Hmmm... There was a problem saving your scores - please have another go.', 'mode': mode }
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
  if request.method == 'POST':
    player = get_object(Player, key)
    if player:
      player.active = False
      player.put()
      response_dict = { 'status': True, 'message' : 'Player successfully deleted.' }
      return HttpResponse(simplejson.dumps(response_dict), mimetype='application/json')
    else:
      response_dict = { 'status': False, 'message' : "Hmm... We couldn't find that player. Please have another go." }
      return HttpResponse(simplejson.dumps(response_dict), mimetype='application/json')
  else:
    return HttpResponseRedirect('/')

def paypal(request):
  return render_to_response(request, 'pingpong/paypal.html')

def upgrade(request):
  return render_to_response(request, 'pingpong/upgrade.html')
  
def terms(request):
  return render_to_response(request, 'pingpong/terms.html')

@login_required
def player_stats(request, key):
  player = get_object(Player, key)
  # Calculate the player's ranking on the fly
  singles_ranking = 0
  doubles_ranking = 0
  singles_players = Player.gql("WHERE owner = :owner AND active = True ORDER BY singles_ranking_points DESC, name",
                                owner=request.user)
  for sp in singles_players:
    singles_ranking += 1
    if sp.key == player.key:
      break
  doubles_players = Player.gql("WHERE owner = :owner AND active = True ORDER BY doubles_ranking_points DESC, name",
                                owner=request.user)
  for dp in doubles_players:
    doubles_ranking += 1
    if dp.key == player.key:
      break

  player_games = [] # Load game history
  # Find all teams where player is player1 (no gql OR operator)
  teams = Team.gql("WHERE player1 = :player", player=player)
  for t in teams:
    games = Game.gql("WHERE team1 = :team", team=t)
    for g in games:
      player_games.append(g)
    games = Game.gql("WHERE team2 = :team", team=t)
    for g in games:
      player_games.append(g)
  # Find all teams where player is player2 (no gql OR operator)
  teams = Team.gql("WHERE player2 = :player", player=player)
  for t in teams:
    games = Game.gql("WHERE team1 = :team", team=t)
    for g in games:
      player_games.append(g)
    games = Game.gql("WHERE team2 = :team", team=t)
    for g in games:
      player_games.append(g)
  player_games.sort(cmp=lambda x,y: cmp(x.date_played, y.date_played), reverse=True)

  return render_to_response(request, 'pingpong/player_stats.html',
    { 'player': player, 'singles_ranking': singles_ranking, 'doubles_ranking': doubles_ranking, 
    'games': player_games[:20] })
