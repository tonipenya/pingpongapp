# -*- coding: utf-8 -*-
import logging
import urllib
import urllib2

from django.utils import simplejson
from django.forms.fields import email_re
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from ragendja.template import render_to_response
from ragendja.dbutils import get_object, db_create, prefetch_references
from ragendja.auth.decorators import staff_only
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, HttpResponseServerError, \
  HttpResponseRedirect
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.create_update import create_object, delete_object, \
  update_object
from pingpong.models import Player, Team, Game, PlayerGame, UserSettings
from pingpong.forms import make_player_form, ContactForm
from pingpong.rankings import DefaultRankingSystem
from paypal.standard.forms import PayPalPaymentsForm

mobile_uas = [
  'w3c ','acs-','alav','alca','amoi','audi','avan','benq','bird','blac',
  'blaz','brew','cell','cldc','cmd-','dang','doco','eric','hipt','inno',
  'ipaq','java','jigs','kddi','keji','leno','lg-c','lg-d','lg-g','lge-',
  'maui','maxo','midp','mits','mmef','mobi','mot-','moto','mwbp','nec-',
  'newt','noki','oper','palm','pana','pant','phil','play','port','prox',
  'qwap','sage','sams','sany','sch-','sec-','send','seri','sgh-','shar',
  'sie-','siem','smal','smar','sony','sph-','symb','t-mo','teli','tim-',
  'tosh','tsm-','upg1','upsi','vk-v','voda','wap-','wapa','wapi','wapp',
  'wapr','webc','winw','winw','xda','xda-', ]
 
mobile_ua_hints = [ 'SymbianOS', 'Opera Mini', 'iPhone' ]

def is_mobile_browser(request):
  mobile_browser = False
  ua = request.META['HTTP_USER_AGENT'].lower()[0:4]
  if (ua in mobile_uas):
    mobile_browser = True
  else:
    for hint in mobile_ua_hints:
      if request.META['HTTP_USER_AGENT'].find(hint) > 0:
        mobile_browser = True
  return mobile_browser

@staff_only
def dash(request):
  total_accounts = UserSettings.all().count()
  paying_accounts = UserSettings.all().filter("has_paid_subscription = ", True).count()
  free_accounts = UserSettings.all().filter("free_account = ", True).count()
  context = { "total_accounts": total_accounts, "paying_accounts": paying_accounts,
    "free_accounts": free_accounts }
  return render_to_response(request, 'pingpong/dash.html', context)

def index(request):
  if request.user.is_authenticated():
    settings = get_user_settings(request.user)
    singles_players = Player.gql("WHERE owner = :owner AND active = True ORDER BY singles_ranking_points DESC, name",
                                  owner=request.user)
    doubles_players = Player.gql("WHERE owner = :owner AND active = True ORDER BY doubles_ranking_points DESC, name",
                                  owner=request.user)
    return render_to_response(request, 'pingpong/main.html', {
      'trial_expired': settings.trial_expired(), 'trial_days_left': settings.trial_days_left(),
      'in_trial_period': (not settings.has_paid_subscription and not settings.free_account), 
      'singles_players': singles_players, 'doubles_players': doubles_players, 
      'isMobile': True if is_mobile_browser(request) else False })
  else:
    from django.conf import settings
    if is_mobile_browser(request):
		  return render_to_response(request, 'pingpong/mobile.html', { 'price': settings.MONTHLY_PRICE })
    else:
		  return render_to_response(request, 'pingpong/index.html', { 'price': settings.MONTHLY_PRICE })
			
def get_user_settings(user):
  key_name = '%s_settings' % str(user.key())
  settings = UserSettings.get_by_key_name(key_name)
  if settings is None:
    settings = UserSettings(key_name=key_name, user=user)
    settings.put()
  return settings

def home(request):
  from django.conf import settings
  if request.user.is_authenticated():
    return render_to_response(request, 'pingpong/index.html', { 'price': settings.MONTHLY_PRICE })
  else:
    return HttpResponseRedirect('/')

def login(request):
  if request.method == 'POST':
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if user is not None:
      if user.is_active:
        auth_login(request, user)
        return HttpResponseRedirect('/')
    if is_mobile_browser(request):
      return render_to_response(request, 'pingpong/mobile.html',
        { 'login_error': 'Your username or password was invalid',
          'previous_username': request.POST['username'] })
    else:
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
          if player:
            if len(v.strip()) > 0:
              player.name = v # Value is the updated player name
              player.put()
            else:
              errors[str(k)[:-7]] = 'Invalid name'

      if len(errors) == 0:
        response_dict = { 'status': True, 'message': 'Settings successfully saved.' }
      else:
        response_dict = { 'status': False, 'message': 'Hmmm... There was a problem saving your settings - please have another go.',
          'errors': errors }
      return HttpResponse(simplejson.dumps(response_dict), mimetype='application/json')
    except:
      logging.exception('There was a problem saving settings')
      response_dict = { 'status': False, 'message': 'Hmmm... There was a problem saving your settings - please have another go.',
        'errors': errors }
    return HttpResponse(simplejson.dumps(response_dict), mimetype='application/json')

def is_valid_email(email):
    return True if email_re.match(email) else False

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
      save_player_games(game, t1p1, t1p2, t2p1, t2p2, t1s, t2s)
      doubles = (t1p1 != None and t1p2 != None and t2p1 != None and t2p2 != None)
      if doubles:
        mode = 'doubles'
      ranking_system = DefaultRankingSystem()
      ranking_system.save_game(t1p1=t1p1, t1p2=t1p2, t2p1=t2p1, t2p2=t2p2, 
        t1s=t1s, t2s=t2s, t1=t1, t2=t2, game=game, doubles=doubles)
      response_dict = { 'status': True, 'message': 'Scores successfully saved.', 
        'mode': mode, 'game': str(game.key()) }
    except:
      logging.exception('There was a problem adding scores')
      response_dict = { 'status': False, 'message' : 'Hmmm... There was a problem saving your scores - please have another go.', 'mode': mode }
    return HttpResponse(simplejson.dumps(response_dict), mimetype='application/json')

def save_player_games(game, p1, p2, p3, p4, t1s, t2s):
  if p1 != None:
    db_create(PlayerGame, player=p1, game=game, date_played=game.date_played, won=game.won(p1),
              t1p1=p1, t1p2=p2, t2p1=p3, t2p2=p4, team1_points=t1s, team2_points=t2s)
  if p2 != None:
    db_create(PlayerGame, player=p2, game=game, date_played=game.date_played, won=game.won(p2),
              t1p1=p1, t1p2=p2, t2p1=p3, t2p2=p4, team1_points=t1s, team2_points=t2s)
  if p3 != None:
    db_create(PlayerGame, player=p3, game=game, date_played=game.date_played, won=game.won(p3),
              t1p1=p1, t1p2=p2, t2p1=p3, t2p2=p4, team1_points=t1s, team2_points=t2s)
  if p4 != None:
    db_create(PlayerGame, player=p4, game=game, date_played=game.date_played, won=game.won(p4),
              t1p1=p1, t1p2=p2, t2p1=p3, t2p2=p4, team1_points=t1s, team2_points=t2s)

@login_required
def undo_score(request, key):
  if request.method == 'POST':
    try:
      game = get_object(Game, key)
      if game:
        mode = 'doubles' if game.doubles() else 'singles'
        delete_player_games(game)
        ranking_system = DefaultRankingSystem()
        ranking_system.undo_save_game(game)
        response_dict = { 'status': True, 'message': 'Done.', 'mode': mode }
      else:
        response_dict = { 'status': False, 'message': "Hmmm... We couldn't find that game - sorry." }
    except:
      logging.exception('There was a problem undoing the addition of the game')
      response_dict = { 'status': False, 'message' : 'Hmmm... There was a problem undoing your game - sorry.' }
    return HttpResponse(simplejson.dumps(response_dict), mimetype='application/json')
  else:
    return HttpResponseRedirect('/')

def delete_player_games(game):
  pgs = PlayerGame.gql("WHERE game = :game", game=game)
  for pg in pgs:
    pg.delete()

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

@login_required
def upgrade(request):
  from django.conf import settings
  return render_to_response(request, 'pingpong/upgrade.html',
    { 'price': settings.MONTHLY_PRICE })

@login_required
def paypal(request):
  from django.conf import settings
  vals = {
    "cmd": "_xclick-subscriptions",
    "business": settings.PAYPAL_RECEIVER_EMAIL,
    "item_number": "1",
    "item_name": "PingPongNinja.com - $%s/mo - cancel anytime" % settings.MONTHLY_PRICE,
    "no_shipping": "1",
    "rm": "2",
    "a3": settings.MONTHLY_PRICE,
    "p3": "1",
    "t3": "M",
    "src": "1",
    "sra": "1",
    "no_note": "1",
    "custom": str(request.user.key()),
    "page_style": "primary",
    "return_url": "http://www.pingpongninja.com/",
    "cancel_return": "http://www.pingpongninja.com/",
    "notify_url": settings.PAYPAL_NOTIFY_URL,
  }
  form = PayPalPaymentsForm(initial=vals)
  context = { "form": form }
  return render_to_response(request, 'pingpong/paypal.html', context)

def terms(request):
  from django.conf import settings
  return render_to_response(request, 'pingpong/terms.html', { 'price': settings.MONTHLY_PRICE })
  
def privacy(request):
  return render_to_response(request, 'pingpong/privacy.html')
  
def about(request):
  return render_to_response(request, 'pingpong/about.html')

def contact(request):
  if request.method == 'POST':
    form = ContactForm(request.POST)
    if form.is_valid():
      subject = 'PingPongNinja contact form submission'
      feedback = form.cleaned_data['feedback']
      email = form.cleaned_data['email']
      recipients = ['support@pingpongninja.com']
      from django.conf import settings
      msg = EmailMessage(subject=subject, body=feedback, from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients, headers= { 'Reply-To': email })
      msg.send()
      return HttpResponseRedirect('/thanks/')
  else:
    form = ContactForm()
  return render_to_response(request, 'pingpong/contact.html', { 'form': form, })

def thanks(request):
  return render_to_response(request, 'pingpong/thanks.html')

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

  games = []
  pgs = PlayerGame.gql("WHERE player = :player ORDER BY date_played DESC LIMIT 20", player=player)
  for pg in pgs:
    games.append(pg)
  return render_to_response(request, 'pingpong/player_stats.html',
    { 'player': player, 'singles_ranking': singles_ranking, 
      'doubles_ranking': doubles_ranking, 'games': games })
