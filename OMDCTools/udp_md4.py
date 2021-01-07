#!/usr/bin/env python3

import socket
import binascii
import struct

def main():
  MCAST_GRP = '239.1.1.24' #'239.1.1.84' 
  MCAST_PORT = 51004 # 53550
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
  try:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  except AttributeError:
    pass
  sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32) 
  sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

  sock.bind((MCAST_GRP, MCAST_PORT))
  host = '10.55.9.189' # socket.gethostbyname(socket.gethostname())
  sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(host))
  sock.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, 
                   socket.inet_aton(MCAST_GRP) + socket.inet_aton(host))

  while 1:
    try:
      data, addr = sock.recvfrom(1024)
    except  e:
      print('Expection')
    pkg_size, msg_count, filters, seq_num, sending_time=struct.unpack('<HBbIQ', data)
    hexdata = binascii.hexlify(data)
    print('Data = %s, msg_count=%d, seq_num=%d' % (hexdata, msg_count, seq_num))

if __name__ == '__main__':
  main()
