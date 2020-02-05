from enum import unique, Enum


@unique
class ExecType(Enum):
    NEW = '0'
    CANCEL = '4'
    AMEND = '5'
    REJECT = '8'
    EXPIRE = 'C'
    TRADE = 'F'
    TRADE_CANCEL = 'H'
    TRIGGERED_OR_ACTIVATED_BY_SYSTEM = 'L'
    CANCEL_REJECT = 'X'
    AMEND_REJECT = 'Y'
