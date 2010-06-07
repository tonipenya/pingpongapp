from pingpong.models import Player, Team, Game

"""
The default ranking system used. Alternative ranking systems may evolve...
"""
class DefaultRankingSystem:
  
  def save_game(self, t1p1, t1p2, t2p1, t2p2, t1s, t2s, t1, t2, game, doubles=False):
    if t1s > t2s:
      if doubles:
        t1p1.doubles_games_won += 1
        t2p1.doubles_games_lost += 1
        t1p2.doubles_games_won += 1
        t2p2.doubles_games_lost += 1
      else:
        t1p1.singles_games_won += 1
        t2p1.singles_games_lost += 1
    else:
      if doubles:
        t2p1.doubles_games_won += 1
        t1p1.doubles_games_lost += 1
        t2p2.doubles_games_won += 1
        t1p2.doubles_games_lost += 1
      else:
        t2p1.singles_games_won += 1
        t1p1.singles_games_lost += 1
    team1_ranking_points = 0
    team2_ranking_points = 0
    if doubles:
      self.reset_doubles_last_movements(t1p1.owner)
      team1_ranking_points = (t1p1.doubles_ranking_points + t1p2.doubles_ranking_points) / 2
      team2_ranking_points = (t2p1.doubles_ranking_points + t2p2.doubles_ranking_points) / 2
    else:
      self.reset_singles_last_movements(t1p1.owner)
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

  def reset_singles_last_movements(self, user):
    players = Player.gql("WHERE owner = :owner", owner=user)
    for p in players:
      if p.singles_last_movement != 0.0:
        p.singles_last_movement = 0.0
        p.put()

  def reset_doubles_last_movements(self, user):
    players = Player.gql("WHERE owner = :owner", owner=user)
    for p in players:
      if p.doubles_last_movement != 0.0:
        p.doubles_last_movement = 0.0
        p.put()
