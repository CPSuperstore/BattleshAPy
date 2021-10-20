"""
This module contains the game class which represents a single bot playing a single game
"""
import abc
import datetime
import time
import typing

import requests

import BattleshAPy.game_object.island_game_object as island_game_object
import BattleshAPy.game_object.player_game_object as player_game_object
import BattleshAPy.game_object.ship_game_object as ship_game_object
import BattleshAPy.game_object_collection.island_collection as island_collection
import BattleshAPy.game_object_collection.player_collection as player_collection
import BattleshAPy.game_object_collection.ship_collection as ship_collection
import BattleshAPy.store_object.ship_store_object as ship_store_object
import BattleshAPy.utils as utils


class Game(abc.ABC):
    """
    The game class represents a bot in a game.
    It is an abstract class as there are some methods which need to be overridden

    Mandatory methods to override:
    - on_turn_start -- Called each time it becomes my turn. The turn is automatically ended after this is called

    Optional methods to override:
    - on_create -- Called once after the object has been initialized.
    """
    def __init__(self, game_id: str, token: str):
        """
        :param game_id:
        :param token:
        """
        self.game_id = game_id
        self.token = token

        self.url_base = utils.get_url_base()

        self.game_size = None           # type: typing.Tuple[int, int]
        self.turn_length = None         # type: datetime.time

        self.players = player_collection.PlayerCollection([])      # type: player_collection.PlayerCollection[player_game_object.Player]
        self.islands = island_collection.IslandCollection([])      # type: island_collection.IslandCollection[island_game_object.Island]

        self.me = None              # type: player_game_object.Player

        self.base_locations = {}

        # test credentials
        self._poll_game_status()

        self.on_create()

    def on_create(self):
        """
        This overridable method is called on object creation
        """

    def _headers(self) -> dict:
        return dict(token=self.token)

    def _poll_game_status(self) -> dict:
        r = requests.get(self.url_base + "/game", headers=self._headers())
        return r.json()

    def get_player_count(self) -> int:
        """
        Returns the number of players still in the game
        """
        status = self._poll_game_status()
        if "players" in status:
            return len(status["players"])

        return len(status["opponents"]) + 1

    def is_game_started(self) -> bool:
        """
        Returns if the game has started
        """
        status = self._poll_game_status()
        return status.get("status", "running").lower() != "waiting"

    def wait_for_game_start(self, poll_every: float = 0.5) -> 'game':
        """
        Blocks until the game has started
        :param poll_every: the interval to poll the server at. Minimum is 0.3s
        :return: this object so chaining is possible
        """
        while True:
            start = time.time()
            if self.is_game_started():
                break

            time.sleep(max([0.3, poll_every - (time.time() - start)]))
            return self

    def wait_for_player_count(self, count: int, poll_every: float = 0.5) -> 'game':
        """
        Blocks until the game has a defined number of players joined
        :param count: number of players
        :param poll_every: the interval to poll the server at. Minimum is 0.3s
        :return: this object so chaining is possible
        """
        while True:
            start = time.time()
            player_count = self.get_player_count()
            if player_count >= count:
                break

            time.sleep(max([0.3, poll_every - (time.time() - start)]))

        return self

    def wait_for_time(self, delay: float) -> 'game':
        """
        Blocks for a defined amount of time. This is a wrapper for time.sleep()
        It was included for its ability to be chained, and completeness
        :return: this object so chaining is possible
        """
        time.sleep(delay)
        return self

    def start_game(self) -> 'game':
        """
        Sends the command to start the game
        """
        requests.put(self.url_base + "/game", headers=self._headers())
        return self

    def is_my_turn(self) -> bool:
        """
        Determines if it is my turn or not
        """
        r = requests.get(self.url_base + "/turn", headers=self._headers())
        return r.json()["is_me"]

    def get_current_turn(self) -> player_game_object.Player:
        """
        Returns the player whose turn it currently is
        """
        r = requests.get(self.url_base + "/turn", headers=self._headers())
        return self.players.get_by_id(r.json()["turn"])

    def _end_turn(self):
        requests.post(self.url_base + "/turn", headers=self._headers())

    @abc.abstractmethod
    def on_turn_start(self):
        """
        This abstract method is called at the start of each turn
        The turn is automatically ended after this method is called
        """

    def _update_islands(self):
        r = requests.get(self.url_base + "/island", headers=self._headers())
        self.islands.from_json(r.json())

    def _update_ships(self):
        r = requests.get(self.url_base + "/ship", headers=self._headers())

        player_data = r.json()
        for p in player_data:
            p["ships"] = ship_collection.ShipCollection([]).from_json(p["ships"])
            p["game"] = self
            p["x"], p["y"] = self.base_locations[p["id"]]

        self.players.from_json(player_data)
        self.me = self.players.get_by_attribute("me", True)
        self.me.is_me = True

        for p in self.players.objects:
            p.post_process_ships()

    def play(self, poll_every: float = 0.5):
        """
        This method begins the main loop of the game
        This should only be called AFTER the game has started
        :param poll_every: the interval to poll the server at. Minimum is 0.3s
        """
        self._update_islands()

        status = self._poll_game_status()

        self.base_locations.clear()
        self.base_locations[status["me"]["id"]] = status["me"]["base"]["x"], status["me"]["base"]["y"]
        for o in status["opponents"]:
            self.base_locations[o["id"]] = o["base"]["x"], o["base"]["y"]

        self.game_size = status["board_size"]
        self.turn_length = datetime.datetime.strptime(status["turn_length"], '%H:%M:%S').time()

        while True:
            start = time.time()
            if self.is_my_turn():
                self._update_ships()
                self.on_turn_start()
                self._end_turn()

            time.sleep(max([0.3, poll_every - (time.time() - start)]))

    def buy_ship(self, ship_id: str) -> ship_game_object.Ship:
        """
        Purchase a ship by its ID
        Note that named constants are available with all the default ship IDs
        :param ship_id: the ID of the ship you wish to purchase
        :return: the newly purchased ship
        """
        r = requests.post(self.url_base + "/store", headers=self._headers(), json={
            "ship": ship_id
        })
        self._update_ships()
        return self.me.ships.get_by_id(r.json()["id"])

    def get_store_inventory(self) -> typing.List[ship_store_object.ShipStore]:
        """
        Returns the entire game inventory as a list of ShipStore objects
        The ShipStore object has a method 'purchase' to buy it, OR
        you can pass its ID into the 'buy_ship' method of this object
        """
        result = []
        r = requests.get(self.url_base + "/store", headers=self._headers())
        for item in r.json():
            item["game"] = self
            result.append(ship_store_object.ShipStore(**item))

        return result

    def move_ship(self, ship: typing.Union[str, ship_game_object.Ship], x: int, y: int):
        """
        Moves the provided ship object to the specified coordinates
        :param ship: either the id of the ship you wish to move, OR the ship object
        :param x:
        :param y:
        """
        if isinstance(ship, ship_game_object.Ship):
            ship = ship.id

        requests.post(
            self.url_base + "/ship", headers=self._headers(), json={
                "action": "move",
                "position": [x, y],
                "ship": ship
            }
        )

    def move_ship_relative(self, ship: typing.Union[str, ship_game_object.Ship], x: int, y: int):
        """
        Moves the provided ship object relative to its current position
        :param ship: either the id of the ship you wish to move, OR the ship object
        :param x:
        :param y:
        """
        if isinstance(ship, ship_game_object.Ship):
            ship = ship.id

        requests.post(
            self.url_base + "/ship", headers=self._headers(), json={
                "action": "move",
                "relative": [x, y],
                "ship": ship
            }
        )

    def shoot_ship(self, ship: typing.Union[str, ship_game_object.Ship], x: int, y: int, repeat: int = 1):
        """
        Fires the gun of the provided ship to the specified position
        :param ship: either the id of the ship you wish to move, OR the ship object
        :param x:
        :param y:
        :param repeat: The number of times to fire the gun
        """
        if isinstance(ship, ship_game_object.Ship):
            ship = ship.id

        requests.post(
            self.url_base + "/ship", headers=self._headers(), json={
                "action": "shoot",
                "position": [x, y],
                "ship": ship,
                "repeat": repeat
            }
        )

    def shoot_ship_relative(self, ship: typing.Union[str, ship_game_object.Ship], x: int, y: int, repeat: int = 1):
        """
        Fires the gun of the provided ship relative to the current position of the ship
        :param ship: either the id of the ship you wish to move, OR the ship object
        :param x:
        :param y:
        :param repeat: The number of times to fire the gun
        """
        if isinstance(ship, ship_game_object.Ship):
            ship = ship.id

        requests.post(
            self.url_base + "/ship", headers=self._headers(), json={
                "action": "shoot",
                "relative": [x, y],
                "ship": ship,
                "repeat": repeat
            }
        )
