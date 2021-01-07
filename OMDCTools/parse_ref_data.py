#!/usr/bin/env python3

import socket
import binascii
import struct
import codecs

def main():
    decoder = codecs.getdecoder('utf_16_le')
    with open("rf.bin", 'rb') as fp:
        while True:
            msg_header = fp.read(16)
            if msg_header == b'':
                break
            pkt_size, msg_count, filter, seq_num, send_time = struct.unpack('<HB1sIQ', msg_header)
            #print('pkt_size=%d, msg_count=%d, seq_num=%d send_time=%d \n' % (pkt_size, msg_count, seq_num, send_time))
            if pkt_size == 0:
                continue
            data = fp.read(pkt_size-16)
            #while True:
            if len(data) == 0:
                break
            for i in range(msg_count):
                if len(data) == 0:
                    break
                msg_size, msg_type = struct.unpack('<2H', data[0:4])
                #print('msg_size=%d, msg_type=%d, i=%d, data len=%d \n' % (msg_size, msg_type, i, len(data)))
                # print('len = %d, msg_header = %s \n' % (pkg_size_val, msg_header))
                if msg_type == 0:
                    continue
                # print('msg_size=%d, msg_type=%d, data len=%d \n' % (msg_size, msg_type, len(data)))
                if msg_type == 10:
                    print('Market Definition')
                elif msg_type == 11:
                    print('Security Definition')
                    security_code, market_code, isin_code, instrument_type, product_type, filter, spread_trable_code,security_short_name, currecy_code=struct.unpack('<I4s12s4sB1s2s40s3s', data[4:75])
                    print('security_code=%d, market_code=%s,  isin_code=%s, instrument_type=%s, product_type=%s, spread_trable_code=%s, security_short_name=%s, currecy_code=%s, big5=%s, gb=%s' % (security_code, market_code.decode('utf-8').strip(), isin_code.decode('utf-8').strip(), instrument_type.decode('utf-8').strip(), product_type, spread_trable_code.decode('utf-8').strip(), security_short_name.decode('utf-8').strip(), currecy_code.decode('utf-8'), decoder(data[75:135])[0].strip(), decoder(data[135:195])[0].strip()))
                    if security_code == 5203:
                        return
                elif msg_type == 13:
                    print('Liquidity Provider')
                elif msg_type == 14:
                    print('Currency Rate')
                else:
                    print
                data = data[msg_size:]
                #msg_count, filters, seq_num, sending_time, msg_header, msg_type=struct.unpack('<BbIQ2H', data[0:18])
                #hexdata = binascii.hexlify(data)
                #print('Data = %s, msg_count=%d, seq_num=%d, msg_header=%d, msg_type=%d' % (hexdata, msg_count, seq_num, msg_header, msg_type))

if __name__ == '__main__':
  main()
