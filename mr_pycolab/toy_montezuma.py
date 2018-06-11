from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import curses
import sys
import os.path
import copy

import numpy as np
import six

from pycolab import ascii_art
from pycolab import human_ui
from pycolab import things as plab_things
from pycolab import cropping
from pycolab.prefab_parts import sprites as prefab_sprites

__PATH__ = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(__PATH__, './toy_montezuma.txt')) as f:
  GAME_ART = [l for l in f.readlines() if l]
  max_l = max(len(l) for l in GAME_ART)
  GAME_ART = [l + '`' * (max_l - len(l)) for l in GAME_ART]

FG_COLOURS = {
    'X': (200, 200, 999),
    'D': (300, 500, 100),
    '#': (100, 100, 100),
    '`': (100, 100, 100),
    '|': (100, 100, 100),
    '-': (100, 100, 100),
    '+': (100, 100, 100),
    ' ': (700, 700, 700),
    '.': (500, 400, 500),
    ',': (400, 500, 500),
    'G': (300, 500, 900),
    'K': (100, 100, 100),
}
BG_COLOURS = {
    'K': (500, 500, 100),
    'X': (1000, 0, 0),
    '#': (0, 0, 0),
    '`': (0, 0, 0),
    '|': (0, 0, 0),
    '+': (0, 0, 0),
    '-': (0, 0, 0),
    'D': (0, 0, 1000),
    'G': (0, 0, 0),
}


def make_game():
  return ascii_art.ascii_art_to_game(
      GAME_ART, what_lies_beneath=' ',
      sprites={'P': PlayerSprite},
      drapes={'K': KeyDrape,
              'D': DoorDrape},
      update_schedule=['P', 'K', 'D'],
  )


class PlayerSprite(prefab_sprites.MazeWalker):
  """A `Sprite` for our player.
  """

  def __init__(self, corner, position, character):
    """Inform superclass that we can't walk through walls."""
    super(PlayerSprite, self).__init__(
        corner, position, character, impassable='#+-|D',
        confined_to_board=True)

  def update(self, actions, board, layers, backdrop, things, the_plot):
    del backdrop, things   # Unused.

    # Apply motion commands.
    if actions == 0:    # walk upward?
      self._north(board, the_plot)
    elif actions == 1:  # walk downward?
      self._south(board, the_plot)
    elif actions == 2:  # walk leftward?
      self._west(board, the_plot)
    elif actions == 3:  # walk rightward?
      self._east(board, the_plot)

    # die if it hits a red-flag cell.
    if layers['X'][self.position]:
      the_plot.terminate_episode()

    # yeah!!
    if layers['G'][self.position]:
      the_plot.add_reward(10000.0)
      the_plot.terminate_episode()


class KeyDrape(plab_things.Drape):

  def update(self, actions, board, layers, backdrop, things, the_plot):

    py, px = things['P'].position.row, things['P'].position.col

    if self.curtain[py, px]:
      # grab the key
      self.curtain[py, px] = False
      the_plot.add_reward(100.0)

      # increase the number of key in the inventory.
      the_plot['num_keys'] = the_plot.get('num_keys', 0) + 1


class DoorDrape(plab_things.Drape):

  def update(self, actions, board, layers, backdrop, things, the_plot):
    dy = [+1, -1, 0, 0]
    dx = [0, 0, +1, -1]

    py, px = things['P'].position.row, things['P'].position.col

    if the_plot.get('num_keys', 0) > 0:
      # if has a key, try to open it
      if actions is not None and 0 <= actions < 4:
        if self.curtain[py - dy[actions], px - dx[actions]]:
          # open the door
          self.curtain[py - dy[actions], px - dx[actions]] = False
          the_plot.add_reward(400.0)
          # one key is taken off.
          the_plot['num_keys'] -= 1


class RoomCropper(cropping.ObservationCropper):

  def __init__(self, rows, cols, to_track):
    super(RoomCropper, self).__init__()
    self._rows = rows
    self._cols = cols

    if not isinstance(to_track, six.string_types):
      raise TypeError("to_track should be a single character")
    self._to_track = copy.copy(to_track)
    self._pad_char = '`'

  def crop(self, observation):
    py, px = self._engine.things[self._to_track].position
    py = int(py // self._rows) * self._rows
    px = int(px // self._cols) * self._cols

    return self._do_crop(
      observation,
      py, px,
      py + self._rows, px + self._cols
    )



import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--full-observation', action='store_true', default=False)


def main(args):
  # Build a four-rooms game.
  game = make_game()

  if args.full_observation:
    croppers = []
  else:
    # partial observation as in the original MontezumaRevenge
    croppers = [RoomCropper(rows=11, cols=11, to_track='P')]

  # Make a CursesUi to play it with.
  ui = human_ui.CursesUi(
      keys_to_actions={curses.KEY_UP: 0, curses.KEY_DOWN: 1,
                       curses.KEY_LEFT: 2, curses.KEY_RIGHT: 3,
                       -1: 4},
      delay=200,
      colour_fg=FG_COLOURS,
      colour_bg=BG_COLOURS,
      croppers=croppers,
  )

  # Let the game begin!
  ui.play(game)


if __name__ == '__main__':
  args = parser.parse_args()
  main(args)
