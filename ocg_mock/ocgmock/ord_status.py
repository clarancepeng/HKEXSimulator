from enum import IntEnum, unique


@unique
class OrdStatus(IntEnum):
    NEW = 0
    PARTIALLY_FILLED = 1
    FILLED = 2
    CANCELLED = 4
    PENDING_CANCEL = 6
    REJECTED = 8
    PENDING_NEW = 10
    EXPIRED = 12
    PENDING_AMEND = 14
