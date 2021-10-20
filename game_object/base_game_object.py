"""
This module contains the base game object
"""
import abc


class BaseGameObject(abc.ABC):
    """
    This is the object which all game objects inherit from
    """
    def __init__(self, id: str, x: int, y: int):
        """
        :param id:
        :param x:
        :param y:
        """
        self.id = id
        self.x = x
        self.y = y

    def distance(self, x: int, y: int) -> int:
        """
        Returns the distance from ths object to the specified point
        :param x:
        :param y:
        :return:
        """
        return abs(self.x - x) + abs(self.y - y)

    def __repr__(self):
        return "<{} id={} x={} y={}>".format(
            self.__class__.__name__, self.id, self.x, self.y
        )
