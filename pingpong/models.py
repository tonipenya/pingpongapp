from google.appengine.ext import db
from django.contrib.auth.models import User

class Player(db.Model):
  owner = db.ReferenceProperty(User, collection_name="player_owner_set")
  name = db.StringProperty(required=True)
  date_created = db.DateTimeProperty(auto_now_add=True)
  ranking_points = db.IntegerProperty(default=100)
  last_movement = db.IntegerProperty(default=0) # Last points gained/lost e.g. +5 or -5

  def display_last_movement(self):
    if self.last_movement == 0:
      return ''
    if self.last_movement > 0:
      return '+%d' % self.last_movement
    else:
      return '%d' % self.last_movement

  def lost_last(self):
    return self.last_movement < 0

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
  date_created = db.DateTimeProperty(auto_now_add=True)
  date_scores_entered = db.DateTimeProperty()
