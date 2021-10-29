class BattleshAPIException(Exception):
    pass


class GameNotStartedException(BattleshAPIException):
    pass


class NotYourTurnException(BattleshAPIException):
    pass


class AlreadyRegisteredException(BattleshAPIException):
    pass


class ShipInTheWayException(BattleshAPIException):
    pass


class InsufficientFundsException(BattleshAPIException):
    pass


class CanNotAccessShipException(BattleshAPIException):
    pass


class OutOfShotsException(BattleshAPIException):
    pass


class CannotAttackHomeBaseException(BattleshAPIException):
    pass


class TargetOutOfRangeException(BattleshAPIException):
    pass


class PositionOccupiedException(BattleshAPIException):
    pass


class TargetOutOfBoundsException(BattleshAPIException):
    pass


class ConflictException(BattleshAPIException):
    pass


class GameEndedException(BattleshAPIException):
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
