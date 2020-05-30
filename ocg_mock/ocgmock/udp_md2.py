import socket
import sys
import struct
import time
import random

HOST, PORT = "239.1.1.3", 51001
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if __name__ == "__main__":
    max_volume = 500000
    level1_max_value = 5000
    while True:
        # security_id = 700, 3888
        security_id = 700
        round_lot = 100
        tick_size = 200
        base_px = random.randrange(400000, 450000, tick_size)
        data=struct.pack('<HBcIQ', 1000, 2, b'\0', 1, 0)
        data+=struct.pack('2HI3sB', 492, 53, security_id, b'', 20)
        data+=struct.pack('Q2IH2B4sQ2IH2B4s', random.randrange(round_lot, level1_max_value, round_lot),base_px,1,0,1,0,b'',random.randrange(round_lot, max_volume, round_lot),base_px-tick_size,1,0,2,0,b'')
        data+=struct.pack('Q2IH2B4sQ2IH2B4s', random.randrange(round_lot, max_volume, round_lot),base_px-2*tick_size,1,0,3,0,b'',random.randrange(round_lot, max_volume, round_lot),base_px-3*tick_size,1,0,4,0,b'')
        data+=struct.pack('Q2IH2B4sQ2IH2B4s', random.randrange(round_lot, max_volume, round_lot),base_px-4*tick_size,1,0,5,0,b'',random.randrange(round_lot, max_volume, round_lot),base_px-5*tick_size,1,0,6,0,b'')
        data+=struct.pack('Q2IH2B4sQ2IH2B4s', random.randrange(round_lot, max_volume, round_lot),base_px-6*tick_size,1,0,7,0,b'',random.randrange(round_lot, max_volume, round_lot),base_px-7*tick_size,1,0,8,0,b'')
        data+=struct.pack('Q2IH2B4sQ2IH2B4s', random.randrange(round_lot, max_volume, round_lot),base_px-8*tick_size,1,0,9,0,b'',random.randrange(round_lot, max_volume, round_lot),base_px-9*tick_size,1,0,10,0,b'')
        data+=struct.pack('Q2IH2B4sQ2IH2B4s', random.randrange(round_lot, level1_max_value, round_lot),base_px+tick_size,1,1,1,0,b'',random.randrange(round_lot, max_volume, round_lot),base_px+2*tick_size,1,1,2,0,b'')
        data+=struct.pack('Q2IH2B4sQ2IH2B4s', random.randrange(round_lot, max_volume, round_lot),base_px+3*tick_size,1,1,3,0,b'',random.randrange(round_lot, max_volume, round_lot),base_px+4*tick_size,1,1,4,0,b'')
        data+=struct.pack('Q2IH2B4sQ2IH2B4s', random.randrange(round_lot, max_volume, round_lot),base_px+5*tick_size,1,1,5,0,b'',random.randrange(round_lot, max_volume, round_lot),base_px+6*tick_size,1,1,6,0,b'')
        data+=struct.pack('Q2IH2B4sQ2IH2B4s', random.randrange(round_lot, max_volume, round_lot),base_px+7*tick_size,1,1,7,0,b'',random.randrange(round_lot, max_volume, round_lot),base_px+8*tick_size,1,1,8,0,b'')
        data+=struct.pack('Q2IH2B4sQ2IH2B4s', random.randrange(round_lot, max_volume, round_lot),base_px+9*tick_size,1,1,9,0,b'',random.randrange(round_lot, max_volume, round_lot),base_px+10*tick_size,1,1,10,0,b'')
        security_id = 3888
        round_lot = 1000
        tick_size = 50
        base_px = random.randrange(23000, 25000, tick_size)
        data+=struct.pack('2HI3sB', 492, 53, security_id, b'', 20)
        data+=struct.pack('Q2IH2B4sQ2IH2B4s', random.randrange(round_lot, level1_max_value, round_lot),base_px,1,0,1,0,b'',random.randrange(round_lot, max_volume, round_lot),base_px-tick_size,1,0,2,0,b'')
        data+=struct.pack('Q2IH2B4sQ2IH2B4s', random.randrange(round_lot, max_volume, round_lot),base_px-2*tick_size,1,0,3,0,b'',random.randrange(round_lot, max_volume, round_lot),base_px-3*tick_size,1,0,4,0,b'')
        data+=struct.pack('Q2IH2B4sQ2IH2B4s', random.randrange(round_lot, max_volume, round_lot),base_px-4*tick_size,1,0,5,0,b'',random.randrange(round_lot, max_volume, round_lot),base_px-5*tick_size,1,0,6,0,b'')
        data+=struct.pack('Q2IH2B4sQ2IH2B4s', random.randrange(round_lot, max_volume, round_lot),base_px-6*tick_size,1,0,7,0,b'',random.randrange(round_lot, max_volume, round_lot),base_px-7*tick_size,1,0,8,0,b'')
        data+=struct.pack('Q2IH2B4sQ2IH2B4s', random.randrange(round_lot, max_volume, round_lot),base_px-8*tick_size,1,0,9,0,b'',random.randrange(round_lot, max_volume, round_lot),base_px-9*tick_size,1,0,10,0,b'')
        data+=struct.pack('Q2IH2B4sQ2IH2B4s', random.randrange(round_lot, level1_max_value, round_lot),base_px+tick_size,1,1,1,0,b'',random.randrange(round_lot, max_volume, round_lot),base_px+2*tick_size,1,1,2,0,b'')
        data+=struct.pack('Q2IH2B4sQ2IH2B4s', random.randrange(round_lot, max_volume, round_lot),base_px+3*tick_size,1,1,3,0,b'',random.randrange(round_lot, max_volume, round_lot),base_px+4*tick_size,1,1,4,0,b'')
        data+=struct.pack('Q2IH2B4sQ2IH2B4s', random.randrange(round_lot, max_volume, round_lot),base_px+5*tick_size,1,1,5,0,b'',random.randrange(round_lot, max_volume, round_lot),base_px+6*tick_size,1,1,6,0,b'')
        data+=struct.pack('Q2IH2B4sQ2IH2B4s', random.randrange(round_lot, max_volume, round_lot),base_px+7*tick_size,1,1,7,0,b'',random.randrange(round_lot, max_volume, round_lot),base_px+8*tick_size,1,1,8,0,b'')
        data+=struct.pack('Q2IH2B4sQ2IH2B4s', random.randrange(round_lot, max_volume, round_lot),base_px+9*tick_size,1,1,9,0,b'',random.randrange(round_lot, max_volume, round_lot),base_px+10*tick_size,1,1,10,0,b'')
        sock.sendto(data, (HOST, PORT))
        time.sleep(1)
