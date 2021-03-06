"""
This module contains the game class which represents a single bot playing a single game
"""
import abc
import datetime
import os.path
import random
import time
import traceback
import typing
import json

import requests

import BattleshAPy.game_object.island_game_object as island_game_object
import BattleshAPy.game_object.player_game_object as player_game_object
import BattleshAPy.game_object.ship_game_object as ship_game_object
import BattleshAPy.game_object_collection.island_collection as island_collection
import BattleshAPy.game_object_collection.player_collection as player_collection
import BattleshAPy.game_object_collection.ship_collection as ship_collection
import BattleshAPy.store_object.ship_store_object as ship_store_object
import BattleshAPy.utils as utils
import BattleshAPy.exceptions as exceptions
import BattleshAPy.local_data.player_ship as local_player_ship


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
        self.running = True
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

        self.local_player_ship_data = {}
        self._load_local_player_ship_data()

        self.on_create()

    def on_create(self):
        """
        This overridable method is called on object creation
        """

    def _headers(self) -> dict:
        return dict(token=self.token)

    def _poll_game_status(self) -> dict:
        r = requests.get(self.url_base + "/game", headers=self._headers())
        self._handle_error(r)
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

    def wait_for_game_start(self, poll_every: float = 0.5) -> 'Game':
        """
        Blocks until the game has started
        :param poll_every: the interval to poll the server at. Minimum is 0.3s
        :return: this object so chaining is possible
        """
        while True:
            start = time.time()
            if self.is_game_started():
                return self

            time.sleep(max([0.3, poll_every - (time.time() - start)]))

    def wait_for_player_count(self, count: int, poll_every: float = 0.5) -> 'Game':
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

    def wait_for_time(self, delay: float) -> 'Game':
        """
        Blocks for a defined amount of time. This is a wrapper for time.sleep()
        It was included for its ability to be chained, and completeness
        :return: this object so chaining is possible
        """
        time.sleep(delay)
        return self

    def start_game(self) -> 'Game':
        """
        Sends the command to start the game
        """
        r = requests.put(self.url_base + "/game", headers=self._headers())
        self._handle_error(r)
        return self

    def is_my_turn(self) -> bool:
        """
        Determines if it is my turn or not
        """
        r = requests.get(self.url_base + "/turn", headers=self._headers())
        self._handle_error(r)
        return r.json()["is_me"]

    def get_current_turn(self) -> player_game_object.Player:
        """
        Returns the player whose turn it currently is
        """
        r = requests.get(self.url_base + "/turn", headers=self._headers())
        self._handle_error(r)
        return self.players.get_by_id(r.json()["turn"])

    def _end_turn(self):
        r = requests.post(self.url_base + "/turn", headers=self._headers())
        try:
            self._handle_error(r)
        except exceptions.NotYourTurnException:
            pass

    @abc.abstractmethod
    def on_turn_start(self):
        """
        This abstract method is called at the start of each turn
        The turn is automatically ended after this method is called
        """

    def _update_islands(self):
        r = requests.get(self.url_base + "/island", headers=self._headers())
        self._handle_error(r)
        self.islands.from_json(r.json())

    def flush_local_player_ship_data(self):
        with open("local_data.json", 'w') as f:
            data = {k: v.to_dict() for k, v in self.local_player_ship_data.items()}
            f.write(json.dumps(data))

    def _load_local_player_ship_data(self):
        if not os.path.isfile("local_data.json"):
            self.local_player_ship_data = {}
            return

        with open("local_data.json", 'r') as f:
            try:
                for ship_id, data in json.loads(f.read()).items():
                    self.local_player_ship_data[ship_id] = local_player_ship.PlayerShip.from_dict(data)

            except json.JSONDecodeError:
                self.local_player_ship_data = {}

    def _update_ships(self):
        r = requests.get(self.url_base + "/ship", headers=self._headers())
        self._handle_error(r)

        player_data = r.json()
        for p in player_data:
            if p["me"] is True:
                for s in p["ships"]:
                    if s["id"] not in self.local_player_ship_data:
                        self.local_player_ship_data[s["id"]] = local_player_ship.PlayerShip(s["id"])

                    s["player_ship"] = self.local_player_ship_data[s["id"]]

            else:
                for s in p["ships"]:
                    s["player_ship"] = None

            p["ships"] = ship_collection.ShipCollection([]).from_json(p["ships"])
            p["game"] = self
            p["x"], p["y"] = self.base_locations[p["id"]]

        self.players.from_json(player_data)
        self.me = self.players.get_by_attribute("me", True)
        self.me.is_me = True

        for p in self.players.objects:
            p.post_process_ships()

    def _run_autopilot_cycle(self):
        retry = []
        for ship in self.me.ships:
            try:
                if ship.local_player_ship.target_x is not None or ship.local_player_ship.target_y is not None:
                    ship.move_ship_relative(*ship.get_next_move())

                    if ship.local_player_ship.target_x is None and ship.local_player_ship.target_y is None:
                        self.on_ship_arrive(ship)

            except exceptions.PositionOccupiedException:
                retry.append(ship)

        retry.reverse()

        for ship in retry:
            try:
                ship.move_ship_relative(*ship.get_next_move())
            except exceptions.PositionOccupiedException:
                pass

    def get_free_islands(self) -> island_collection.IslandCollection:
        result = []
        for island in self.islands.objects:
            if not self.is_position_occupied(island.x, island.y):
                result.append(island)

        return island_collection.IslandCollection(result)

    def get_free_untargeted_islands(self) -> island_collection.IslandCollection:
        result = []
        for island in self.islands.objects:
            if not self.is_position_occupied_or_targeted(island.x, island.y):
                result.append(island)

        return island_collection.IslandCollection(result)

    def is_position_occupied(self, x: int, y: int) -> ship_game_object.Ship:
        for p in self.players.objects:
            for ship in p.ships.objects:
                if ship.x == x and ship.y == y:
                    return ship

    def is_position_occupied_or_targeted(self, x: int, y: int) -> ship_game_object.Ship:
        for p in self.players.objects:
            for ship in p.ships.objects:
                if (
                        ship.x == x and ship.y == y
                ) or (
                        ship.local_player_ship.target_x == x and ship.local_player_ship.target_y == y
                ) or (
                        ship.local_player_ship.target_y == y and ship.local_player_ship.target_x is None and ship.x == x
                ):
                    return ship

    def play(self, poll_every: float = 0.5):
        """
        This method begins the main loop of the game
        This should only be called AFTER the game has started
        :param poll_every: the interval to poll the server at. Minimum is 0.3s
        """
        self._update_islands()

        status = self._poll_game_status()

        self.base_locations.clear()
        try:
            self.base_locations[status["me"]["id"]] = status["me"]["base"]["x"], status["me"]["base"]["y"]
        except KeyError:
            raise exceptions.GameNotStartedException(
                "The game has not been started yet. Could not begin playing the game. "
                "Either call 'start_game' if you created the game or call "
                "'wait_for_game_start' to block until the game starts."
            )

        for o in status["opponents"]:
            self.base_locations[o["id"]] = o["base"]["x"], o["base"]["y"]

        self.game_size = status["board_size"]
        self.turn_length = datetime.datetime.strptime(status["turn_length"], '%H:%M:%S').time()

        ran_game_start_event = False

        while self.running:
            start = time.time()

            try:
                if self.is_my_turn():
                    try:
                        self._update_ships()
                        self._run_autopilot_cycle()

                        if not ran_game_start_event:
                            self.on_game_start()
                            ran_game_start_event = True

                        self.on_turn_start()
                    except exceptions.GameEndedException:
                        break

                    except Exception:
                        traceback.print_exc()

                    self._end_turn()

                time.sleep(max([0.3, poll_every - (time.time() - start)]))

            except exceptions.GameEndedException:
                break

    def buy_ship(self, ship_id: str, auto_move: bool = True) -> ship_game_object.Ship:
        """
        Purchase a ship by its ID
        Note that named constants are available with all the default ship IDs
        :param ship_id: the ID of the ship you wish to purchase
        :param auto_move: in the event a ship is in the way, do we automatically reposition that ship?
        :return: the newly purchased ship
        """
        r = requests.post(self.url_base + "/store", headers=self._headers(), json={
            "ship": ship_id
        })
        try:
            self._handle_error(r)
        except exceptions.ShipInTheWayException as e:
            if auto_move:
                ship = self.me.ships.get_by_id(r.json()["ship"])
                ship.move_ship(*self.get_free_position_in_radius(
                    self.me.x, self.me.y, ship.units_left
                ))
                return self.buy_ship(ship_id, auto_move=False)

            else:
                raise e

        self._update_ships()
        return self.me.ships.get_by_id(r.json()["id"])

    def _handle_error(self, r: requests.Response):
        if r.status_code == 409:
            response = r.json()
            try:
                raise exceptions.CODE_EXCEPTION_LOOKUP[response["code"]](response["message"])
            except KeyError:
                raise exceptions.ConflictException(response["message"])

        if r.status_code == 404:
            self.running = False
            raise exceptions.GameEndedException("The game has ended. Please terminate this script.")

    def get_store_inventory(self) -> typing.List[ship_store_object.ShipStore]:
        """
        Returns the entire game inventory as a list of ShipStore objects
        The ShipStore object has a method 'purchase' to buy it, OR
        you can pass its ID into the 'buy_ship' method of this object
        """
        result = []
        r = requests.get(self.url_base + "/store", headers=self._headers())
        self._handle_error(r)
        for item in r.json():
            item["game"] = self
            result.append(ship_store_object.ShipStore(**item))

        return result

    def get_min_attribute_from_store(self, attribute: str) -> ship_store_object.ShipStore:
        smallest = None
        for ship in self.get_store_inventory():
            if smallest is None:
                smallest = ship
            else:
                if getattr(ship, attribute) < getattr(smallest, attribute):
                    smallest = ship

        return smallest

    def get_max_attribute_from_store(self, attribute: str) -> ship_store_object.ShipStore:
        largest = None
        for ship in self.get_store_inventory():
            if largest is None:
                largest = ship
            else:
                if getattr(ship, attribute) > getattr(largest, attribute):
                    largest = ship

        return largest

    def get_cheapest_ship(self) -> ship_store_object.ShipStore:
        return self.get_min_attribute_from_store("price")

    def get_weakest_ship(self) -> ship_store_object.ShipStore:
        return self.get_min_attribute_from_store("max_hp")

    def get_smallest_shot_damage_ship(self) -> ship_store_object.ShipStore:
        return self.get_min_attribute_from_store("shot_damage")

    def get_smallest_shot_range_ship(self) -> ship_store_object.ShipStore:
        return self.get_min_attribute_from_store("shot_range")

    def get_smallest_shots_per_turn_ship(self) -> ship_store_object.ShipStore:
        return self.get_min_attribute_from_store("shots_per_turn")

    def get_smallest_units_per_turn_ship(self) -> ship_store_object.ShipStore:
        return self.get_min_attribute_from_store("units_per_turn")

    def get_most_expensive_ship(self) -> ship_store_object.ShipStore:
        return self.get_max_attribute_from_store("price")

    def get_strongest_ship(self) -> ship_store_object.ShipStore:
        return self.get_max_attribute_from_store("max_hp")

    def get_highest_shot_damage_ship(self) -> ship_store_object.ShipStore:
        return self.get_max_attribute_from_store("shot_damage")

    def get_highest_shot_range_ship(self) -> ship_store_object.ShipStore:
        return self.get_max_attribute_from_store("shot_range")

    def get_highest_shots_per_turn_ship(self) -> ship_store_object.ShipStore:
        return self.get_max_attribute_from_store("shots_per_turn")

    def get_highest_units_per_turn_ship(self) -> ship_store_object.ShipStore:
        return self.get_max_attribute_from_store("units_per_turn")

    def move_ship(self, ship: typing.Union[str, ship_game_object.Ship], x: int, y: int) -> typing.Tuple[int, int]:
        """
        Moves the provided ship object to the specified coordinates
        :param ship: either the id of the ship you wish to move, OR the ship object
        :param x:
        :param y:
        """
        if isinstance(ship, ship_game_object.Ship):
            ship = ship.id

        r = requests.post(
            self.url_base + "/ship", headers=self._headers(), json={
                "action": "move",
                "position": [x, y],
                "ship": ship
            }
        )

        self._handle_error(r)

        position = r.json()["position"]
        try:
            ship = self.me.ships.get_by_id(ship)
            ship.x, ship.y = position
        except ValueError:
            pass
        return position

    def move_ship_relative(self, ship: typing.Union[str, ship_game_object.Ship], x: int, y: int) -> typing.Tuple[int, int]:
        """
        Moves the provided ship object relative to its current position
        :param ship: either the id of the ship you wish to move, OR the ship object
        :param x:
        :param y:
        """
        if isinstance(ship, ship_game_object.Ship):
            ship = ship.id

        r = requests.post(
            self.url_base + "/ship", headers=self._headers(), json={
                "action": "move",
                "relative": [x, y],
                "ship": ship
            }
        )

        self._handle_error(r)

        position = r.json()["position"]
        try:
            ship = self.me.ships.get_by_id(ship)
            ship.x, ship.y = position
        except ValueError:
            pass
        return position

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

        r = requests.post(
            self.url_base + "/ship", headers=self._headers(), json={
                "action": "shoot",
                "position": [x, y],
                "ship": ship,
                "repeat": repeat
            }
        )
        self._handle_error(r)

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

        r = requests.post(
            self.url_base + "/ship", headers=self._headers(), json={
                "action": "shoot",
                "relative": [x, y],
                "ship": ship,
                "repeat": repeat
            }
        )
        self._handle_error(r)

    def on_game_start(self):
        """
        This event is triggered before the game starts
        It is run once and only once
        """

    @staticmethod
    def distance(x1: int, y1: int, x2: int, y2: int) -> int:
        """
        Returns the distance between the specified points
        """
        return abs(x2 - x1) + abs(y2 - y1)

    def get_free_position_in_radius(self, x: int, y: int, r: int) -> typing.Tuple[int, int]:
        min_pos = (x - r, y - r)
        max_pos = (x + r, y + r)

        center_x = x
        center_y = y

        player_positions = [(p.x, p.y) for p in self.players.objects]

        for x in range(min_pos[0], max_pos[0] + 1):
            for y in range(min_pos[1], max_pos[1] + 1):
                if not (0 <= x <= self.game_size[0] and 0 <= y <= self.game_size[1]):
                    continue

                if self.distance(x, y, center_x, center_y) > r:
                    continue

                if (x, y) in player_positions:
                    continue

                for player in self.players.objects:
                    try:
                        player.ships.get_at_position(x, y)
                        break

                    except ValueError:
                        pass
                else:
                    return x, y

        raise ValueError("There are no free spaces available in a {} unit radius from {}".format(
            r, (center_x, center_y)
        ))

    def get_all_free_positions_in_radius(self, x: int, y: int, r: int) -> typing.List[typing.Tuple[int, int]]:
        min_pos = (x - r, y - r)
        max_pos = (x + r, y + r)

        center_x = x
        center_y = y

        result = []

        player_positions = [(p.x, p.y) for p in self.players.objects]

        for x in range(min_pos[0], max_pos[0] + 1):
            for y in range(min_pos[1], max_pos[1] + 1):
                if not (0 <= x <= self.game_size[0] and 0 <= y <= self.game_size[1]):
                    continue

                if self.distance(x, y, center_x, center_y) > r:
                    continue

                if (x, y) in player_positions:
                    continue

                for player in self.players.objects:
                    try:
                        player.ships.get_at_position(x, y)
                        break

                    except ValueError:
                        pass
                else:
                    result.append((x, y))

        return result

    def get_n_free_positions_in_radius(self, x: int, y: int, r: int, n: int) -> typing.List[typing.Tuple[int, int]]:
        return self.get_all_free_positions_in_radius(x, y, r)[:n]

    def order_positions_by_distance(self, positions: typing.List[typing.Tuple[int, int]], x: int, y: int) -> typing.List[typing.Tuple[int, int]]:
        positions.sort(key=lambda o: self.distance(*o, x, y), reverse=False)
        return positions

    def get_captured_islands(self) -> island_collection.IslandCollection:
        islands = []
        for island in self.islands.objects:
            try:
                self.me.ships.get_at_position(island.x, island.y)
                islands.append(island)
            except ValueError:
                pass

        return island_collection.IslandCollection(islands)

    def on_ship_arrive(self, ship: ship_game_object.Ship):
        pass

    def get_other_players(self) -> player_collection.PlayerCollection:
        players = []

        for i in self.players.objects:
            if i.me is False:
                players.append(i)

        return player_collection.PlayerCollection(players)

    def get_random_other_player(self) -> player_game_object.Player:
        return random.choice(self.get_other_players().objects)
