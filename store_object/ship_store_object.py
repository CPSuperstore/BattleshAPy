"""
This module represents an item for sale in the store
"""
import typing

if typing.TYPE_CHECKING:
    import BattleshAPy.game as game_object


class ShipStore:
    """
    This object represents an item for sale in the store
    WARNING: Do not directly instantiate this class! Let the library handle that
    """
    def __init__(
            self, custom: bool, id: str, max_hp: int, name: str, price: int, shot_damage: int, shot_range: int,
            shots_per_turn: int, units_per_turn: int, game: 'game_object.Game'
    ):
        """
        :param custom:
        :param id:
        :param max_hp:
        :param name:
        :param price:
        :param shot_damage:
        :param shot_range:
        :param shots_per_turn:
        :param units_per_turn:
        :param game:
        """
        self.custom = custom
        self.id = id
        self.max_hp = max_hp
        self.name = name
        self.price = price
        self.shot_damage = shot_damage
        self.shot_range = shot_range
        self.shots_per_turn = shots_per_turn
        self.units_per_turn = units_per_turn
        self.game = game

    def purchase(self):
        """
        Executes the purchase of this ship from the store
        And returns the ship
        """
        return self.game.buy_ship(self.id)

    def __repr__(self):
        return "<ShipStore name={} price={} custom={}>".format(self.name, self.price, self.custom)
