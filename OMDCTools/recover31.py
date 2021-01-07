#!/usr/bin/env python3

import socket
import time
import struct
import binascii

MaxBytes=1024*1024
host ='10.1.90.42'
port = 55455

# packet head(16bit): PktSize(Uint16, len=2), MsgCount(Uint8, len=1), Filter(String, len=1), SeqNum=(Uint32, len=4), SendTime(Long, len=4)
# Msg=Packet Head + MsgSize(Uint16, len=2), MsgType(Uint16, len=2, Value=101), UserName(String, len=12)
def build_logon():
    return struct.pack('<HB1sIQHH12s', 32, 1, b'', 0, 0, 16, 101, b'T-VALUABLE1')

# Msg=Packet Head + MsgSize(Uint16, len=2), MsgType(Uint16, len=2, Value=201), ChannelID(Uint16, len=2), Filter(String, len=2), BeginSeqNum(Uint32, len=4), EndSeqNum(Uint32, len=4)
def build_retransmission_request():
    return struct.pack('<HB1sIQ3H2s2I', 32, 1, b'', 0, 0, 16, 201, 31, b'', 1, 10000)

def main():
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#    client.bind(('10.55.9.162', 11111))
    client.settimeout(30)
    client.connect((host,port))

    sendBytes = client.send(build_logon())
    if sendBytes<=0:
        print('No Data Send')
    recvData = client.recv(MaxBytes)
    if not recvData:
        print('No data received, exit!')
    else:
        localTime = time.asctime( time.localtime(time.time()))
        pkt_size, msg_count, filters, seq_num, sending_time,msg_size, msg_type, session_status, filters2=struct.unpack('<HBbIQ2HB3s',recvData)
        hexdata = binascii.hexlify(recvData)
        print('Data = %s\n' % (hexdata))
        print('pkt_size=%d, msg_count=%d, seq_num=%d, send_time=%d, msg_size=%d,msg_type=%d,session_status=%d' % (pkt_size, msg_count, seq_num, sending_time, msg_size, msg_type, session_status))

        print(localTime, ' Got bytes=:',len(recvData))
        print(recvData)

    sendBytes = client.send(build_retransmission_request())
    if sendBytes<=0:
        print('No Data Send')
    with open("data_channel_31.bin.dat", 'wb') as fp:
        while True:
            recvData = client.recv(MaxBytes)
            if len(recvData) == 0:
                print('all received!!!')
                break
            if not recvData:
                print('No data received, exit!')
                break
            else:
                localTime = time.asctime( time.localtime(time.time()))
                hexdata = binascii.hexlify(recvData)
                print('Data = %s\n' % (hexdata))
                # pkt_size, msg_count, filters, seq_num, sending_time,msg_size, msg_type, channel_id, retrans_status, filters2, begin_seq_num, end_seq_num=struct.unpack('<HBbIQ3HB1s2I',recvData[0:32])
                # print('pkt_size=%d, msg_count=%d, seq_num=%d, send_time=%d, msg_size=%d,msg_type=%d,channel_id=%d, retrans_status=%d' % (pkt_size, msg_count, seq_num, sending_time, msg_size, msg_type, channel_id, retrans_status))
 
                print(localTime, ' Got bytes=:',len(recvData))
                print(recvData)
                fp.write(recvData)
                fp.flush()
    fp.close()

    client.close()

if __name__ == '__main__':
    main()
