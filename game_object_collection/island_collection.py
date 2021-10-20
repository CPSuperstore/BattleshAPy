"""
This module contains the island collection
"""
import BattleshAPy.game_object_collection.base_object_collection as base_object_collection
import BattleshAPy.game_object.island_game_object as island_game_object


class IslandCollection(base_object_collection.BaseObjectCollection):
    """
    This object represents a collection of islands
    """
    def __init__(self, objects):
        super().__init__(island_game_object.Island, objects)
