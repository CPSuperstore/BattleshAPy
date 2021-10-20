"""
This module contains the player collection
"""
import BattleshAPy.game_object_collection.base_object_collection as base_object_collection
import BattleshAPy.game_object.player_game_object as player_game_object


class PlayerCollection(base_object_collection.BaseObjectCollection):
    """
    This object represents a collection of player
    """
    def __init__(self, objects):
        super().__init__(player_game_object.Player, objects)
