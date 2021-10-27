"""
This module contains a collection of generics
"""
import typing


T = typing.TypeVar('T')


class BaseObjectCollection(typing.Generic[T]):
    """
    This object represents a collection of generics
    WARNING: Do not instantiate this object directly. The library will handle this
    """
    def __init__(self, object_type, objects: typing.List[T]):
        """
        :param object_type:
        :param objects:
        """
        self.objects = objects              # type: typing.List[T]
        self.object_type = object_type

    def get_all_by_distance(self, x: int, y: int) -> typing.List[typing.Tuple[T, int]]:
        """
        Returns all the objects in this collection sorted by their distance from the specified point
        They are returned in a 2d array in the format [ [object 1, distance 1], [object 2, distance 2], ... ]
        :param x:
        :param y:
        """
        objects = [(o, o.distance(x, y)) for o in self.objects]
        objects.sort(key=lambda o: o[1], reverse=False)

        return objects

    def get_all_in_radius(self, x: int, y: int, r: int) -> typing.List[typing.Tuple[T, int]]:
        return list(filter(lambda ship: ship[1] <= r, self.get_all_by_distance(x, y)))

    def get_nearest(self, x: int, y: int) -> typing.Tuple[T, int]:
        """
        Returns the nearest object to the specified location in the format [object, distance]
        :param x:
        :param y:
        """
        return self.get_all_by_distance(x, y)[0]

    def get_n_nearest(self, x: int, y: int, n: int) -> typing.List[typing.Tuple[T, int]]:
        """
        Gets the n nearest objects to the specified location
        They are returned in a 2d array in the format [ [object 1, distance 1], [object 2, distance 2], ... ]
        :param x:
        :param y:
        :param n:
        :return:
        """
        return self.get_all_by_distance(x, y)[:n]

    def get_by_attribute(self, attribute: str, value) -> T:
        """
        Returns the first object which has the specified attribute,
        AND the value of the attribute equals the specified value
        Note that objects which do not have the specified attribute will not be included in the result
        :param attribute:
        :param value:
        """
        for obj in self.objects:
            if hasattr(obj, attribute):
                if getattr(obj, attribute) == value:
                    return obj

        raise ValueError("Could not find object with {} {}".format(attribute, value))

    def get_all_by_attribute(self, attribute: str, value) -> typing.List[T]:
        """
        Returns all the objects which have the specified attribute,
        AND the value of the attribute equals the specified value
        Note that objects which do not have the specified attribute will not be included in the result
        :param attribute:
        :param value:
        """
        result = []
        for obj in self.objects:
            if hasattr(obj, attribute):
                if getattr(obj, attribute) == value:
                    result.append(obj)

        return result

    def get_at_position(self, x: int, y: int) -> T:
        """
        Returns the object which is located at the specified position
        :param x:
        :param y:
        """
        for obj in self.objects:
            if int(x) == int(obj.x) and int(y) == int(obj.y):
                return obj

        raise ValueError("Could not find object at {}, {}".format(x, y))

    def get_by_id(self, id: str):
        """
        Returns the object with the specified ID
        :param id:
        :return:
        """
        return self.get_by_attribute("id", id)

    def from_json(self, data: list, clear_current: bool = True) -> 'BaseObjectCollection':
        """
        This method flushes the current objects with a JSON object
        :param data: the data to flush
        :param clear_current: if existing objects should be purged first. Default is True
        :return: this object so it can be chained
        """
        if clear_current:
            self.objects.clear()

        for d in data:
            self.objects.append(self.object_type(**d))

        return self

    def __repr__(self):
        return "<{} objects={}>".format(
            self.__class__.__name__, len(self.objects)
        )

    def __next__(self):
        return next(self.objects)

    def __iter__(self):
        return iter(self.objects)
