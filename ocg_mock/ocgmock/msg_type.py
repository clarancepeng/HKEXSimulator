from enum import IntEnum, unique


@unique
class MsgType(IntEnum):
    HEART_BEAT = 0
    TEST_REQUEST = 1
    RESEND_REQUEST = 2
    REJECT = 3
    SEQUENCE_RESET = 4
    LOGON = 5
    LOGOUT = 6
    LOOKUP_REQUEST = 7
    LOOKUP_RESPONSE = 8
    BUSINESS_MESSAGE_REJECT = 9
    EXECUTION_REPORT = 10
    NEW_ORDER_SINGLE = 11
    ORDER_CANCEL_REPLACE_REQUEST = 12
    ORDER_CANCEL_REQUEST = 13
    MASS_CANCEL_REQUEST = 14
    ORDER_MASS_CANCEL_REPORT = 15
    QUOTE = 16
    QUOTE_CANCEL = 17
    QUOTE_STATUS_REPORT = 18
    USER_REQUEST = 19
    USER_RESPONSE = 20
    TRADE_CAPTURE_REPORT = 21
    TRADE_CAPTURE_REPORT_ACK = 22
    OBO_CANCEL_REQUEST = 23
    OBO_MASS_CANCEL_REQUEST = 24
    THROTTLE_ENTITLEMENT_REQUEST = 25
    THROTTLE_ENTITLEMENT_RESPONSE = 26
    PARTY_ENTITLEMENT_REQUEST = 27
    PARTY_ENTITLEMENT_REPORT = 28
    ORDER_CANCEL_REJECT = 29

