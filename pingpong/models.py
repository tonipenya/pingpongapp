from datetime import datetime, timedelta
from google.appengine.ext import db
from django.contrib.auth.models import User
from paypal.standard.ipn.signals import *
from ragendja.dbutils import get_object
import logging

def get_user_settings_from_ipn(ipn):
  settings = None
  user_paying = get_object(User, ipn.custom) # custom parameter stores the user key
  if user_paying:
    key_name = '%s_settings' % str(user_paying.key())
    settings = UserSettings.get_by_key_name(key_name)
  return settings

def on_payment_was_successful(sender, **kwargs):
  settings = get_user_settings_from_ipn(sender)
  if settings:
    settings.has_paid_subscription = True
    settings.put()

def on_subscription_cancel(sender, **kwargs):
  settings = get_user_settings_from_ipn(sender)
  if settings:
    settings.has_paid_subscription = False
    settings.put()

def on_subscription_eot(sender, **kwargs):
  settings = get_user_settings_from_ipn(sender)
  if settings:
    settings.has_paid_subscription = False
    settings.put()

payment_was_successful.connect(on_payment_was_successful)
subscription_cancel.connect(on_subscription_cancel)
subscription_eot.connect(on_subscription_eot)

class UserSettings(db.Model):
  # key_name is generated as follows: '%s_settings' % str(user.key())
  user = db.ReferenceProperty(User)
  signup_date = db.DateTimeProperty(auto_now_add=True)
  has_paid_subscription = db.BooleanProperty(default=False)
  free_account = db.BooleanProperty(default=False)
  
  def trial_days_left(self):
    end = self.signup_date + timedelta(days=14) # 14 day trial period
    delta = end - datetime.now()
    return 0 if delta.days <= 0 else delta.days

  def trial_expired(self):
    return self.trial_days_left() == 0

class Player(db.Model):
  owner = db.ReferenceProperty(User, collection_name="player_owner_set")
  name = db.StringProperty(required=True)
  date_created = db.DateTimeProperty(auto_now_add=True)
  singles_ranking_points = db.FloatProperty(default=100.0)
  doubles_ranking_points = db.FloatProperty(default=100.0)
  singles_last_movement = db.FloatProperty(default=0.0)
  doubles_last_movement = db.FloatProperty(default=0.0)
  singles_games_won = db.IntegerProperty(default=0)
  singles_games_lost = db.IntegerProperty(default=0)
  doubles_games_won = db.IntegerProperty(default=0)
  doubles_games_lost = db.IntegerProperty(default=0)
  active = db.BooleanProperty(default=True)

  def singles_games_played(self):
    return self.singles_games_won + self.singles_games_lost

  def doubles_games_played(self):
    return self.doubles_games_won + self.doubles_games_lost

  def display_singles_last_movement(self):
    if self.singles_last_movement == 0:
      return ''
    if self.singles_last_movement > 0:
      return '+%.2f' % self.singles_last_movement
    else:
      return '%.2f' % self.singles_last_movement

  def singles_lost_last(self):
    return self.singles_last_movement < 0

  def display_doubles_last_movement(self):
    if self.doubles_last_movement == 0:
      return ''
    if self.doubles_last_movement > 0:
      return '+%.2f' % self.doubles_last_movement
    else:
      return '%.2f' % self.doubles_last_movement

  def doubles_lost_last(self):
    return self.doubles_last_movement < 0

class Team(db.Model):
  player1 = db.ReferenceProperty(Player, 
    collection_name="player_reference_one_set")
  player2 = db.ReferenceProperty(Player,
    collection_name="player_reference_two_set")
  points = db.FloatProperty()

class Game(db.Model):
  team1 = db.ReferenceProperty(Team,
    collection_name="team_reference_one_set")
  team2 = db.ReferenceProperty(Team,
    collection_name="team_reference_two_set")
  date_played = db.DateTimeProperty(auto_now_add=True)
  p1_ranking_points = db.FloatProperty()
  p2_ranking_points = db.FloatProperty()
  p3_ranking_points = db.FloatProperty()
  p4_ranking_points = db.FloatProperty()

  def won(self, player):
    if self.team1.points > self.team2.points:
      return self.team1.player1 == player or self.team1.player2 == player
    else:
      return self.team2.player1 == player or self.team2.player2 == player

class PlayerGame(db.Model):
  player = db.ReferenceProperty(Player, collection_name="player_reference_player_set")
  game = db.ReferenceProperty(Game)
  
  # TODO: To improve performance, we could just store keys of these players and build
  # a dictionary of unique players...
  
  t1p1 = db.ReferenceProperty(Player, collection_name="player_reference_t1p1_set")
  t1p2 = db.ReferenceProperty(Player, collection_name="player_reference_t1p2_set")
  t2p1 = db.ReferenceProperty(Player, collection_name="player_reference_t2p1_set")
  t2p2 = db.ReferenceProperty(Player, collection_name="player_reference_t2p2_set")
  team1_points = db.FloatProperty()
  team2_points = db.FloatProperty()
  won = db.BooleanProperty()
  date_played = db.DateTimeProperty(auto_now_add=True)
