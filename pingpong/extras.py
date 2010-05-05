
# To create an admin user for local development
from django.contrib.auth.models import User

user = User.get_by_key_name('admin')
if not user or user.username != 'admin' or not (user.is_active and
  user.is_staff and user.is_superuser and user.check_password('admin')):
  user = User(key_name='admin', username='admin', email='admin@localhost',
  first_name='Boss', last_name='Admin', is_active=True, is_staff=True, 
  is_superuser=True)
  user.set_password('admin')
  user.put()

# To reset an account - deletes all games and teams and resets ranking points 
# and last movements for all players
from django.contrib.auth.models import User
from pingpong.models import Player, Team, Game

owner_key_name = '' # Set this to the key name (not the key itself) of the account owner
owner = User.get_by_key_name(owner_key_name)
if owner:
  # Find all players
  players = Player.gql("WHERE owner = :owner", owner=owner)
  for p in players:
    # Find all teams where p is player1 (no gql OR operator)
    teams = Team.gql("WHERE player1 = :player", player=p)
    for t in teams:
      # Delete all games in which t played
      games = Game.gql("WHERE team1 = :team", team=t)
      for g in games:
        g.delete()
      games = Game.gql("WHERE team2 = :team", team=t)
      for g in games:
        g.delete()
      # Delete team
      t.delete()
    # Find all teams where p is player2 (no gql OR operator)
    teams = Team.gql("WHERE player2 = :player", player=p)
    for t in teams:
      # Delete all games in which t played
      games = Game.gql("WHERE team1 = :team", team=t)
      for g in games:
        g.delete()
      games = Game.gql("WHERE team2 = :team", team=t)
      for g in games:
        g.delete()
      # Delete team
      t.delete()
    # Reset games won/lost, ranking points and last movements
    p.doubles_games_lost = 0
    p.doubles_games_won = 0
    p.doubles_last_movement = 0.0
    p.doubles_ranking_points = 100.0
    p.singles_games_lost = 0
    p.singles_games_won = 0
    p.singles_last_movement = 0.0
    p.singles_ranking_points = 100.0
    p.put()
