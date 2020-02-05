import cffi
import os
from sys import platform


class Crc32c:
    def __init__(self):

        ffi = cffi.FFI()
        ffi.cdef("""
            void make_crc_table();
            long calc_checksum(char* msg, int len);
        """)
        try:
            if platform == "linux" or platform == "linux2":
                libcrc = ffi.dlopen(os.getcwd() + "/../libcrc32c.so")
            else:
                libcrc = ffi.dlopen(os.getcwd() + "/../libcrc32c.dll")
        except OSError as ose:
            if platform == "linux" or platform == "linux2":
                libcrc = ffi.dlopen(os.getcwd() + "/libcrc32c.so")
            else:
                libcrc = ffi.dlopen(os.getcwd() + "/libcrc32c.dll")
        libcrc.make_crc_table()
        self.libcrc = libcrc

    def calc_checksum(self, msg):
        return self.libcrc.calc_checksum(msg, len(msg))
