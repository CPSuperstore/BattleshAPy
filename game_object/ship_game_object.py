"""
This module contains the Ship game object
"""
import typing

import BattleshAPy.game_object.base_game_object as base_game_object

if typing.TYPE_CHECKING:
    import BattleshAPy.game_object.player_game_object as player_game_object
    import BattleshAPy.game as game


class Ship(base_game_object.BaseGameObject):
    """
    This object represents a single ship in the game
    WARNING: Do not instantiate this object directly. The library will handle this
    """
    def __init__(
            self, custom: bool, hp: int, id: str, max_hp: int, name: str, position: typing.Tuple[int, int], price: int,
            shot_damage: int, shot_range: int, shots_left: int, shots_per_turn: int, units_left: int,
            units_per_turn: int
    ):
        """
        :param custom:
        :param hp:
        :param id:
        :param max_hp:
        :param name:
        :param position:
        :param price:
        :param shot_damage:
        :param shot_range:
        :param shots_left:
        :param shots_per_turn:
        :param units_left:
        :param units_per_turn:
        """
        super().__init__(id, position[0], position[1])

        self.custom = custom
        self.hp = hp
        self.max_hp = max_hp
        self.name = name
        self.price = price
        self.shot_damage = shot_damage
        self.shot_range = shot_range
        self.shots_left = shots_left
        self.shots_per_turn = shots_per_turn
        self.units_left = units_left
        self.units_per_turn = units_per_turn
        self.player = None              # type: player_game_object.Player

    @property
    def game(self) -> 'game.Game':
        """
        Returns the parent game object
        """
        return self.player.game

    @property
    def is_me(self) -> bool:
        """
        Returns if this ship belongs to me
        """
        return self.player.is_me

    def move_ship(self, x: int, y: int):
        """
        Moves this ship to the specified coordinates
        :param x:
        :param y:
        :return:
        """
        self.game.move_ship(self, x, y)

    def move_ship_relative(self, x: int, y: int):
        """
        Moves the ship relative to its current position
        :param x:
        :param y:
        :return:
        """
        self.game.move_ship_relative(self, x, y)

    def shoot_ship(self, x: int, y: int, repeat: int = 1):
        """
        Causes this ship to fire its gun to the specified position
        :param x:
        :param y:
        :param repeat: the number of times to fire the gun
        :return:
        """
        self.game.shoot_ship(self, x, y, repeat)

    def shoot_ship_relative(self, x: int, y: int, repeat: int = 1):
        """
        Causes this ship to fire its gun relative to its current position
        :param x:
        :param y:
        :param repeat: the number of times to fire the gun
        :return:
        """
        self.game.shoot_ship_relative(self, x, y, repeat)
