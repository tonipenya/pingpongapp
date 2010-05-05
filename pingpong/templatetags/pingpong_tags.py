from django import template

register = template.Library()

@register.filter(name='won')
def won(player, game):
  """Returns a boolean indicating whether a player won a game

  Usage::
      {% if player|won:game %}
      ...
      {% endif %}
  """
  return game.won(player=player)

won.is_safe = True
