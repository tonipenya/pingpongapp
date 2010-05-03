from google.appengine.ext import db
from django.contrib.auth.models import User

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
