"""
This module contains the Player game object
"""
import typing

import BattleshAPy.game_object.base_game_object as base_game_object
import BattleshAPy.game_object_collection.ship_collection as ship_collection

if typing.TYPE_CHECKING:
    import BattleshAPy.game as game_object


class Player(base_game_object.BaseGameObject):
    """
    This object represents a single player in the game
    WARNING: Do not instantiate this object directly. The library will handle this
    """
    def __init__(
            self, hp: int, id: str, x: int, y: int, me: bool, name: str,
            ships: ship_collection.ShipCollection, game: 'game_object.Game', money: int = None
    ):
        """
        :param hp:
        :param id:
        :param x:
        :param y:
        :param me:
        :param name:
        :param ships:
        :param game:
        :param money:
        """
        super().__init__(id, x, y)

        self.hp = hp
        self.me = me
        self.name = name
        self.ships = ships
        self.game = game
        self.money = money

        self.is_me = False

    def post_process_ships(self):
        """
        Additional functionality which is needed to update the ships which belong to the player
        """
        for ship in self.ships.objects:
            ship.player = self
