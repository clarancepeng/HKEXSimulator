import cffi
import os
from sys import platform


class Crc32c:
    def __init__(self, logger):
        self.logger = logger;
        ffi = cffi.FFI()
        ffi.cdef("""
            void make_crc_table();
            long calc_checksum(char* msg, int len);
        """)
        if platform == 'win32':
            try:
                libcrc = ffi.dlopen(os.getcwd() + "/../libcrc32c.dll")
            except OSError as ose:
                libcrc = ffi.dlopen(os.getcwd() + "/libcrc32c.dll")
        elif platform == 'linux' or platform == 'linux2':
            try:
                libcrc = ffi.dlopen(os.getcwd() + "/../libcrc32c.so")
            except OSError as ose:
                libcrc = ffi.dlopen(os.getcwd() + "/libcrc32c.so")
        else:
            logger.error('cannot support platform[%]', platform)
            exit(1)
        libcrc.make_crc_table()
        self.libcrc = libcrc

    def calc_checksum(self, msg):
        return self.libcrc.calc_checksum(msg, len(msg))
