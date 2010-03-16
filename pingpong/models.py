from google.appengine.ext import db
from django.contrib.auth.models import User

class Club(db.Model):
  owner = db.ReferenceProperty(User)
  name = db.StringProperty(required=True)
  date_created = db.DateTimeProperty(auto_now_add=True)

class Player(db.Model):
  club = db.ReferenceProperty(Club)
  first = db.StringProperty(required=True)
  last = db.StringProperty(required=True)
  nick = db.StringProperty(required=True)
  date_created = db.DateTimeProperty(auto_now_add=True)

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
