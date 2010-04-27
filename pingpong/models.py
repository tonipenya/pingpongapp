from google.appengine.ext import db
from django.contrib.auth.models import User

class Player(db.Model):
  owner = db.ReferenceProperty(User, collection_name="player_owner_set")
  name = db.StringProperty(required=True)
  date_created = db.DateTimeProperty(auto_now_add=True)
  singles_ranking_points = db.IntegerProperty(default=100)
  doubles_ranking_points = db.IntegerProperty(default=100)
  singles_last_movement = db.IntegerProperty(default=0) # Last points gained/lost e.g. +5 or -5
  doubles_last_movement = db.IntegerProperty(default=0) # Last points gained/lost e.g. +5 or -5

  def display_singles_last_movement(self):
    if self.singles_last_movement == 0:
      return ''
    if self.singles_last_movement > 0:
      return '+%d' % self.singles_last_movement
    else:
      return '%d' % self.singles_last_movement

  def singles_lost_last(self):
    return self.singles_last_movement < 0

  def display_doubles_last_movement(self):
    if self.doubles_last_movement == 0:
      return ''
    if self.doubles_last_movement > 0:
      return '+%d' % self.doubles_last_movement
    else:
      return '%d' % self.doubles_last_movement

  def doubles_lost_last(self):
    return self.doubles_last_movement < 0

class Team(db.Model):
  player1 = db.ReferenceProperty(Player, 
    collection_name="player_reference_one_set")
  player2 = db.ReferenceProperty(Player,
    collection_name="player_reference_two_set")
  points = db.IntegerProperty()

class Game(db.Model):
  team1 = db.ReferenceProperty(Team,
    collection_name="team_reference_one_set")
  team2 = db.ReferenceProperty(Team,
    collection_name="team_reference_two_set")
  date_played = db.DateTimeProperty(auto_now_add=True)
