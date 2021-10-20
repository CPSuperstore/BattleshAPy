"""
This module contains the Island game object
"""
import BattleshAPy.game_object.base_game_object as base_game_object


class Island(base_game_object.BaseGameObject):
    """
    This object represents a single island in the game
    WARNING: Do not instantiate this object directly. The library will handle this
    """
    def __init__(self, id: str, x: int, y: int, money_per_turn: int, name: str):
        """
        :param id:
        :param x:
        :param y:
        :param money_per_turn:
        :param name:
        """
        super().__init__(id, x, y)
        self.money_per_turn = money_per_turn
        self.name = name
