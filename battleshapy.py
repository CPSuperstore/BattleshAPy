"""
This module contains the object which represents a single bot
From here, the bot can attach to any game given the proper credentials
"""
import requests
import requests.auth as auth

import BattleshAPy.game as game
import BattleshAPy.utils as utils
import BattleshAPy.exceptions as exceptions


class BattleshAPy:
    """
    This object manages a single bot's credentials
    Please be sure you do not have 2 instances of an application running
    which control the same bot in the same game at the same time
    This causes weird things to happen
    """
    def __init__(self, client_id: str, client_secret: str):
        """
        :param client_id:
        :param client_secret:
        """
        self.client_id = client_id
        self.client_secret = client_secret

        self.url_base = utils.get_url_base()

    def create_game(
            self, game_class_ref: game.Game.__class__, length: int = 50, width: int = 50, money_per_turn: int = 100,
            initial_hp: int = 1000, turn_length: int = 5
    ) -> game.Game:
        """
        This method creates a new game which your bot is automatically added to
        Be sure to share the game_id attribute with the people you wish to play with,
        or use it to spectate the game on the website
        :param game_class_ref: The reference to the class you wish to use as the game
        Note that the Game object is abstract and can not be directly instantiated
        :param length:
        :param width:
        :param money_per_turn:
        :param initial_hp:
        :param turn_length:
        """

        r = requests.post(
            self.url_base + "/game", json=dict(
                length=length,
                width=width,
                money_per_turn=money_per_turn,
                initial_hp=initial_hp,
                turn_length=turn_length
            ), auth=auth.HTTPBasicAuth(self.client_id, self.client_secret)
        )

        self._handle_error(r)

        if r.status_code == 200:
            response = r.json()
            return game_class_ref(response["game_id"], response["token"])

    def join_game(self, game_class_ref: game.Game.__class__, game_id: str) -> game.Game:
        """
        This method causes your bot to join a game you have not previously joined by game ID
        :param game_class_ref: The reference to the class you wish to use as the game
        Note that the Game object is abstract and can not be directly instantiated
        :param game_id:
        :return:
        """
        r = requests.post(
            self.url_base + "/game", json=dict(
                game_id=game_id
            ), auth=auth.HTTPBasicAuth(self.client_id, self.client_secret)
        )

        self._handle_error(r)

        if r.status_code == 200:
            response = r.json()
            return game_class_ref(response["game_id"], response["token"])

    def connect_game(self, game_class_ref: game.Game.__class__, game_id: str, token: str) -> game.Game:
        """
        This method attaches you to an existing game where your bot has already joined
        :param game_class_ref: The reference to the class you wish to use as the game
        Note that the Game object is abstract and can not be directly instantiated
        :param game_id:
        :param token:
        :return:
        """
        return game_class_ref(game_id, token)

    def _handle_error(self, r: requests.Response):
        if r.status_code == 409:
            response = r.json()
            raise exceptions.CODE_EXCEPTION_LOOKUP[response["code"]](response["message"])
