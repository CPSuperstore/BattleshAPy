"""
This module contains the ship collection
"""
import BattleshAPy.game_object_collection.base_object_collection as base_object_collection
import BattleshAPy.game_object.ship_game_object as ship_game_object


class ShipCollection(base_object_collection.BaseObjectCollection):
    """
    This object represents a collection of ships
    """
    def __init__(self, objects):
        super().__init__(ship_game_object.Ship, objects)
