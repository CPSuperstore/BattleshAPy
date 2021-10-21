class GameNotStartedException(Exception):
    pass


class NotYourTurnException(Exception):
    pass


class AlreadyRegisteredException(Exception):
    pass


class ShipInTheWayException(Exception):
    pass


class InsufficientFundsException(Exception):
    pass


class CanNotAccessShipException(Exception):
    pass


class OutOfShotsException(Exception):
    pass


class CannotAttackHomeBaseException(Exception):
    pass


class TargetOutOfRangeException(Exception):
    pass


class PositionOccupiedException(Exception):
    pass


class TargetOutOfBoundsException(Exception):
    pass


CODE_EXCEPTION_LOOKUP = {
    1: NotYourTurnException,
    2: AlreadyRegisteredException,
    3: ShipInTheWayException,
    4: InsufficientFundsException,
    5: CanNotAccessShipException,
    6: OutOfShotsException,
    7: CannotAttackHomeBaseException,
    8: TargetOutOfRangeException,
    9: PositionOccupiedException,
    10: TargetOutOfBoundsException
}
