#!/usr/bin/env python3
"""
    HKEX Simulation
    Test Client
    Socket communication
"""

import logging
import os
import socket
import struct
import sys
import yaml
from bitarray import bitarray
from datetime import datetime

from ocgmock .msg_type import MsgType
from ocgmock .util.utils import Utils
from ocgmock .util.crc32c import Crc32c


request_id_seq_no = 1


def init_logger():
    log_format = '%(asctime)-15s %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=log_format)
    # , format='%(asctime)s - %(name)% - %(levelname)s - %(message)s')
    logger_l = logging.getLogger(__name__)
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.DEBUG)
    f_handler = logging.FileHandler('logs/test_client.log')
    f_handler.setLevel(logging.INFO)
    c_format = logging.Formatter(log_format)
    f_format = logging.Formatter(log_format)
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)
    # logger_l.addHandler(c_handler)
    logger_l.addHandler(f_handler)
    return logger_l


def encode_msg_header(msg_type, comp_id, comp_id_s, msg_len, present_map, logger, send_seq_dict):
    seq_num = 1
    logger.info('msg_type=%d comp_id = %s, comp_id type = %s', msg_type, comp_id, type(comp_id))
    # ', present_map = ' , present_map, ', present_map type = ', type(present_map))
    if comp_id_s in send_seq_dict:
        send_seq_dict[comp_id_s] += 1
    else:
        send_seq_dict[comp_id_s] = seq_num
    seq_num = send_seq_dict[comp_id_s]
    return struct.pack('<bHBI2B12s32s', 2, msg_len, msg_type, seq_num, 0, 0, comp_id, present_map.tobytes())


def encode_msg_trailer(msg, crc):
    return msg + struct.pack('<I', crc.calc_checksum(msg))


def build_lookup_request(logger, send_seq_dict, crc):
    present_map = bitarray(32 * 8, endian='big')
    present_map.setall(False)
    comp_id = 'CO99999902'
    # header 54 bytes, trailer 4 bytes
    msg_len = 58
    # Type of service (1 = Order Input)
    present_map[0] = 1
    # Protocol Type (1 = Binary)
    present_map[1] = 1
    msg_len += 1 + 1
    req = encode_msg_header(MsgType.LOOKUP_REQUEST, comp_id.encode('utf-8'), comp_id, msg_len, present_map, logger
                            , send_seq_dict)
    req += struct.pack('<BB', 1, 1)
    return encode_msg_trailer(req, crc)


def build_party_entitle_request(logger, send_seq_dict):
    global request_id_seq_no
    present_map = bitarray(32 * 8, endian='big')
    present_map.setall(False)
    comp_id = 'CO99999902'
    # header 54 bytes, trailer 4 bytes
    msg_len = 58
    # Entitlement request id (21)
    present_map[0] = 1
    msg_len += 21
    req = encode_msg_header(MsgType.PARTY_ENTITLEMENT_REQUEST, comp_id.encode('utf-8'), comp_id, msg_len, present_map, logger
                            , send_seq_dict)
    entitle_request_id = datetime.now().strftime('%H%M%S') + format(str(request_id_seq_no), 's').zfill(5)
    request_id_seq_no = 1
    req += struct.pack('<21s', entitle_request_id.encode('utf-8'))
    return encode_msg_trailer(req)


if __name__ == '__main__':
    logger_ = init_logger()
    send_seq_dict_ = {}
    crc = Crc32c()
    try:
        with open(os.getcwd() + "/../config/lookup-cfg.yaml", 'r') as stream:
            try:
                d = yaml.safe_load(stream)
                print(d)
            except yaml.YAMLError as exc:
                logger_.exception('Could not handle the configuration file!')
                sys.exit(0)
    except FileNotFoundError as exc:
        with open(os.getcwd() + "/config/lookup-cfg.yaml", 'r') as stream:
            try:
                d = yaml.safe_load(stream)
                print(d)
            except yaml.YAMLError as exc:
                logger_.exception('Could not handle the configuration file!')
                sys.exit(0)
    logger_.info('lookup[ip=%s, port= %d]', d['lookup']['ip'], d['lookup']['port'])
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((d['lookup']['ip'], int(d['lookup']['port'])))
    data = build_lookup_request(logger_, send_seq_dict_, crc)
    # data = build_party_entitle_request(logger_, send_seq_dict_, crc)
    sock.send(data)

    while True:
        res = sock.recv(1024)
        if res:
            logger_.info('Receive message length = %d', len(res))
            logger_.info(Utils.print_binary(res))

    sock.close()

