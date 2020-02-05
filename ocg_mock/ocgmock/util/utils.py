import cffi


class Utils:
    def __init__(self):
        pass

    @staticmethod
    def print_binary(msg):
        mm = '\n     '
        for x in range(0, 16):
            mm += format(x, 'x').zfill(2) + ' '
        for x in range(0, len(msg)):
            if x % 16 == 0:
                mm += '\n' + format(x // 16, 'x').zfill(4) + ' '
            mm += format(msg[x], 'x').zfill(2) + ' '
        return mm
