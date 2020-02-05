"""
    HKEX Simulation
    Message handle
"""

import selectors
import struct
from time import sleep
from bitarray import bitarray
from datetime import datetime
from ocgmock.msg_type import MsgType
from ocgmock.exec_type import ExecType
from ocgmock.ord_status import OrdStatus
from ocgmock.util.utils import Utils
from ocgmock.util.crc32c import Crc32c


class Message:
    def __init__(self, selector, sock, addr, keep_running, logger, config_map):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self._recv_buffer = b''
        self._send_buffer = b''
        self.request = b''
        self.response_created = False
        self.send_seq_dict = {}
        self.receive_exp_next_seq_dict = {}
        self.order_seq_no = 1
        self.exec_id_seq_no = 1
        self.report_id_seq_no = 1
        self.keep_running = keep_running
        self.logger = logger
        self.config_map = config_map
        self.crc = Crc32c()
        self.clordid_orderid = {}

    def _set_selector_events_mask(self, mode):
        if mode == 'r':
            events = selectors.EVENT_READ
        elif mode == 'w':
            events = selectors.EVENT_WRITE
        elif mode == 'rw':
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            raise ValueError(f'Invalid events mask mode {repr(mode)}.')
        self.selector.modify(self.sock, events, data=self)

    def _read(self):
        try:
            data = self.sock.recv(4096)
        except BlockingIOError:
            self.logger.error('Read BlockingIOError')
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                self.selector.unregister(self.sock)
                self.sock.close()
                self.keep_running = False
                self.logger.error('Peer closed!')
                raise RuntimeError('Peer closed.')

    def _write(self):
        if self._send_buffer:
            # print('sending', repr(self._send_buffer), 'to', self.addr)
            '''
            try:
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                self.logger.error('BlockingIOError')
                pass
            else:
                self.logger.info('Send length = %d bytes length = %d', sent, len(self._send_buffer))
                self._send_buffer = self._send_buffer[sent:]
            '''
            while len(self._send_buffer) > 3:
                plan_sent = struct.unpack('<H', self._send_buffer[1:3])[0]
                self.logger.info("@@@@@@@@@@@@@@@@@@@@********************* plan sent = %s, msg length = %d", plan_sent
                                 , len(self._send_buffer))
                try:
                    sent = self.sock.send(self._send_buffer[0:plan_sent])
                    sleep(0.01)
                except BlockingIOError:
                    self.logger.error('BlockingIOError')
                    pass
                else:
                    self.logger.info('Send length = %d bytes length = %d', sent, len(self._send_buffer))
                    self._send_buffer = self._send_buffer[sent:]
                # if sent and not self._send_buffer:
                #    self.close()

    def process_events(self, mask):
        self.logger.debug('process_events(), mask = %d', mask)
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()

    def read(self):
        self._read()
        # response message
        self.process_request()

    def write(self):
        if self.request:
            # if not self.response_created:
            self.create_response()

        self._write()

    def close(self):
        self.logger.info('closing connection to %s', self.addr)
        try:
            if self.sock and (self.sock != -1):
                self.selector.unregister(self.sock)
        except ValueError as e1:
            pass
        except Exception as e:
            self.logger.exception('error: selector.unregister() exception for %s', self.addr)
        finally:
            self.sock = None

    def process_request(self):
        self.logger.info('process_request')
        data_len = struct.unpack('<H', self._recv_buffer[1:3])[0]
        if not len(self._recv_buffer) >= data_len:
            self.logger.info('======== truncate some data =======================')
            return
        data = self._recv_buffer[:data_len]
        self._recv_buffer = self._recv_buffer[data_len:]
        self.request = data
        msg_type = self.request[3]
        self.logger.info('received data from %s - msgType = %s', self.addr, msg_type)
        # Set selector to listen for write events, we're done reading.
        self._set_selector_events_mask('w')

    def create_response(self):
        msg_type = self.request[3]
        comp_id = self.request[10:22]
        self.logger.info("MsgType = %s", msg_type)
        # header 54 bytes, trailer 4 bytes
        msg_len = 58
        comp_id_s = comp_id.decode('utf-8')
        present_map = bitarray(32 * 8, endian='big')
        present_map.setall(False)

        if msg_type == MsgType.LOGON:
            self.handle_logon(present_map, msg_len, comp_id, comp_id_s)
            
        elif msg_type == MsgType.HEART_BEAT:
            self.handle_heartbeat(present_map, msg_len, comp_id, comp_id_s)

        elif msg_type == MsgType.LOGOUT:
            self.handle_logout(present_map, msg_len, comp_id, comp_id_s)

        elif msg_type == MsgType.TEST_REQUEST:
            self.handle_test_request(present_map, msg_len, comp_id, comp_id_s)

        elif msg_type == MsgType.RESEND_REQUEST:
            self.handle_resend_request(present_map, msg_len, comp_id, comp_id_s)

        elif msg_type == MsgType.LOOKUP_REQUEST:
            self.handle_lookup(present_map, msg_len, comp_id, comp_id_s)

        elif msg_type == MsgType.NEW_ORDER_SINGLE:
            self.handle_new_order(present_map, msg_len, comp_id, comp_id_s)

        elif msg_type == MsgType.ORDER_CANCEL_REQUEST:
            self.handle_cancel_request(present_map, msg_len, comp_id, comp_id_s)

        elif msg_type == MsgType.ORDER_CANCEL_REPLACE_REQUEST:
            self.handle_amend_request(present_map, msg_len, comp_id, comp_id_s)

        elif msg_type == MsgType.OBO_CANCEL_REQUEST:
            self.handle_obo_cancel_request(present_map, msg_len, comp_id, comp_id_s)

        elif msg_type == MsgType.THROTTLE_ENTITLEMENT_REQUEST:
            self.handle_throttle_entitlement_request(present_map, msg_len, comp_id, comp_id_s)

        elif msg_type == MsgType.PARTY_ENTITLEMENT_REQUEST:
            self.handle_party_entitlement_request(present_map, msg_len, comp_id, comp_id_s)

        else:
            self.logger.info('un-implement for msg_type = ', msg_type)
            self.request = b''
            self._set_selector_events_mask('r')
            return

    def encode_msg_header(self, msg_type, comp_id, comp_id_s, msg_len, present_map):
        seq_num = 1
        self.logger.info('msg_type=%d comp_id = %s, comp_id type = %s', msg_type, comp_id, type(comp_id))
        # ', present_map = ' , present_map, ', present_map type = ', type(present_map))
        if comp_id_s in self.send_seq_dict:
            self.send_seq_dict[comp_id_s] += 1
        else:
            self.send_seq_dict[comp_id_s] = seq_num
        seq_num = self.send_seq_dict[comp_id_s]
        return struct.pack('<bHBI2B12s32s', 2, msg_len, msg_type, seq_num, 0, 0, comp_id, present_map.tobytes())

    def encode_msg_trailer(self, msg):
        ret = msg + struct.pack('<I', self.crc.calc_checksum(msg) & 0xFFFFFFFF)
        self.logger.info(Utils.print_binary(msg))
        return ret

    def handle_throttle_entitlement_request(self, present_map, msg_len, comp_id, comp_id_s):
        mm = 'Throttle Entitlement Response='
        self.logger.info('Throttle Entitlement Request')
        resp_msg_type = MsgType.THROTTLE_ENTITLEMENT_RESPONSE
        pos = 54
        user_req_id = self.request[pos: pos + 20]
        pos += 20
        user_req_type = self.request[pos]
        pos += 1

        user_name = self.request[pos: pos+50]
        self.logger.info('user_req_id=%s user_req_type = %d, user_name = %s', user_req_id.decode('utf-8'),
                         user_req_type, user_name.decode('utf-8'))

        # generate the party entitlement report
        present_map[0], present_map[1], present_map[2] = 1, 1, 1
        msg_body = struct.pack('<20s50sH', user_req_id, user_name, 1)
        msg_len += 20 + 50 + 2
        thro_pre_map = bitarray(2 * 8, endian='big')
        thro_pre_map.setall(False)
        thro_pre_map[0], thro_pre_map[1], thro_pre_map[2], thro_pre_map[3], thro_pre_map[4] = 1, 1, 1, 1, 1
        msg_body += struct.pack('<2sBBHBB', thro_pre_map.tobytes(), 2, 0, 8, 0, 0)
        msg_len += 2 + 1 + 1 + 2 + 1 + 1
        message = self.encode_msg_trailer(self.encode_msg_header(resp_msg_type, comp_id, comp_id_s, msg_len,
                                                                 present_map) + msg_body)
        mm += Utils.print_binary(message)
        self.logger.info(mm)
        # message = b'Response ... '
        self.response_created = True
        self._send_buffer += message
        self.request = b''
        self._set_selector_events_mask('r')

    def handle_party_entitlement_request(self, present_map, msg_len, comp_id, comp_id_s):
        mm = 'Party Entitlement Report='
        self.logger.info('Party Entitlement Request')
        resp_msg_type = MsgType.PARTY_ENTITLEMENT_REPORT
        pos = 54
        entitle_req_id = self.request[pos: pos + 21]

        # generate the party entitlement report
        present_map[0], present_map[1], present_map[2], present_map[3], present_map[4] = 1, 1, 1, 1, 1
        present_map[5] = 1
        entitle_report_id = datetime.now().strftime('%H%M%S') + format(str(self.report_id_seq_no), 's').zfill(5)
        self.report_id_seq_no += 1
        broker_id = '1122'
        request_result, total_no_party_list, last_fragment = 0, 1, 1

        msg_body = struct.pack('<21s21sHHB12s', entitle_report_id.encode('utf-8'), entitle_req_id, request_result
                               , total_no_party_list, last_fragment, broker_id.encode('utf-8'))
        msg_len += 21 + 21 + 2 + 2 + 1 + 12
        message = self.encode_msg_trailer(self.encode_msg_header(resp_msg_type, comp_id, comp_id_s, msg_len,
                                                                 present_map) + msg_body)
        mm += Utils.print_binary(message)
        self.logger.info(mm)
        # message = b'Response ... '
        self.response_created = True
        self._send_buffer += message
        self.request = b''
        self._set_selector_events_mask('r')

    def handle_amend_request(self, present_map, msg_len, comp_id, comp_id_s):
        mm = 'Execution Report='
        self.logger.info('Order Amend Request')
        resp_msg_type = MsgType.EXECUTION_REPORT
        msg_body = b''
        message = self.encode_msg_trailer(self.encode_msg_header(resp_msg_type, comp_id, comp_id_s, msg_len,
                                                                 present_map) + msg_body)
        mm += Utils.print_binary(message)
        self.logger.info(mm)
        # message = b'Response ... '
        self.response_created = True
        self._send_buffer += message
        self.request = b''
        self._set_selector_events_mask('r')

    def handle_obo_cancel_request(self, present_map, msg_len, comp_id, comp_id_s):
        mm = 'Execution Report='
        self.logger.info('Order OBO Cancel Request')
        resp_msg_type = MsgType.EXECUTION_REPORT
        msg_body = b''
        message = self.encode_msg_trailer(self.encode_msg_header(resp_msg_type, comp_id, comp_id_s, msg_len,
                                                                 present_map) + msg_body)
        mm += Utils.print_binary(message)
        self.logger.info(mm)
        # message = b'Response ... '
        self.response_created = True
        self._send_buffer += message
        self.request = b''
        self._set_selector_events_mask('r')

    def handle_cancel_request(self, present_map, msg_len, comp_id, comp_id_s):
        mm = 'Execution Report='
        self.logger.info('Order Cancel Request')
        resp_msg_type = MsgType.EXECUTION_REPORT
        utc_now = datetime.utcnow()
        transact_time = datetime.strftime(utc_now, '%Y%m%d %H:%M:%S.%f')[:-3]
        pm = bitarray(format(self.request[22], 'b').zfill(8), endian='big')
        pm.extend(format(self.request[23], 'b').zfill(8))
        pm.extend(format(self.request[24], 'b').zfill(8))
        pos = 54
        cl_ord_id = self.request[pos: pos + 21]
        pos += 21
        submitting_broker_id = self.request[pos: pos + 12]
        pos += 12
        security_id = self.request[pos: pos + 21]
        pos += 21
        security_id_source = self.request[pos]
        pos += 1
        exch, broker_location_id = None, None
        if pm[4]:
            exch = self.request[pos: pos + 5]
            pos += 5
        if pm[5]:
            broker_location_id = self.request[pos: pos + 11]
            pos += 11
        ord_transact_time = self.request[pos: pos + 25]
        pos += 25
        side = self.request[pos]
        pos += 1
        orig_cl_ord_id = self.request[pos: pos + 21]
        pos += 21
        order_id_in_req = None
        if pm[9]:
            order_id_in_req  = self.request[pos: pos + 21].decode('utf-8')
            pos += 21

        # msg_body = b''
        present_map[0], present_map[1], present_map[2], present_map[3], present_map[4] = 1, 1, 1, 1, 1
        msg_body = struct.pack('<21s12s21sB5s', cl_ord_id, submitting_broker_id, security_id, security_id_source,
                               exch)

        if orig_cl_ord_id in self.clordid_orderid:
            order_id, order_qty, broker_location_id = self.clordid_orderid[orig_cl_ord_id]
        else:
            if order_id_in_req:
                order_id = order_id_in_req
            else:
                order_id = datetime.now().strftime('%H%M%S') + format(str(self.order_seq_no), 's').zfill(5)
            order_qty = None
            broker_location_id = None

        if broker_location_id:
            present_map[5] = 1
            msg_body += struct.pack('<11s', broker_location_id)
            msg_len += 11

        msg_len += 21 + 12 + 21 + 1 + 5
        present_map[6], present_map[7], present_map[8], present_map[9], present_map[11] = 1, 1, 1, 1, 1

        self.order_seq_no += 1
        msg_body += struct.pack('<25sB21s21sB', transact_time.encode('utf-8'), side, orig_cl_ord_id
                                , order_id.encode('utf-8'), b'2'[0])
        msg_len += 25 + 1 + 21 + 21 + 1

        if order_qty:
            present_map[13] = 1
            msg_body += struct.pack('<Q', order_qty)
            msg_len += 8

        present_map[21], present_map[22], present_map[23], present_map[24], present_map[25] = 1, 1, 1, 1, 1
        exec_id = datetime.now().strftime('%H%M%S') + format(str(self.exec_id_seq_no), 's').zfill(5)
        self.exec_id_seq_no += 1
        msg_body += struct.pack('<21sBcQQ', exec_id.encode('utf-8'), OrdStatus.CANCELLED,
                                ExecType.CANCEL.value.encode('utf-8'), 0, 1000)
        msg_len += 21 + 1 + 1 + 8 + 8

        message = self.encode_msg_trailer(self.encode_msg_header(resp_msg_type, comp_id, comp_id_s, msg_len,
                                                                 present_map) + msg_body)
        mm += Utils.print_binary(message)
        self.logger.info(mm)
        # message = b'Response ... '
        self.response_created = True
        self._send_buffer += message
        self.request = b''
        self._set_selector_events_mask('r')

    def handle_lookup(self, present_map, msg_len, comp_id, comp_id_s):
        mm = 'Lookup Response='
        self.logger.info('Lookup Request')
        if self.config_map is None:
            self.logger.info('Unsupported Lookup Request in current Service, Please check your config file')
            self.request = b''
            self._set_selector_events_mask('r')
            return
        primary_ip, primary_port = self.config_map['primary']['ip'], int(self.config_map['primary']['port'])
        secondary_ip, secondary_port = self.config_map['secondary']['ip'], int(self.config_map['secondary']['port'])
        resp_msg_type = MsgType.LOOKUP_RESPONSE
        present_map[0], present_map[3], present_map[4], present_map[5], present_map[6] = 1, 1, 1, 1, 1
        msg_body = struct.pack('<B16sH16sH', 0, primary_ip.encode('utf-8'), primary_port
                               , secondary_ip.encode('utf-8'), secondary_port)
        msg_len += 1 + 16 + 4 + 16 + 4
        message = self.encode_msg_trailer(self.encode_msg_header(resp_msg_type, comp_id, comp_id_s, msg_len,
                                                                 present_map) + msg_body)
        mm += Utils.print_binary(message)
        self.logger.info(mm)
        # message = b'Response ... '
        self.response_created = True
        self._send_buffer += message
        self.request = b''
        self._set_selector_events_mask('r')

    def handle_test_request(self, present_map, msg_len, comp_id, comp_id_s):
        mm = 'HeartBeat for Test Request='
        self.logger.info('Test Request')
        resp_msg_type = MsgType.HEART_BEAT
        pos = 54
        test_req_id = struct.unpack('<H', self.request[pos: pos + 2])[0]
        present_map[0] = 1
        msg_len += 2
        msg_body = struct.pack('<H', test_req_id)
        message = self.encode_msg_trailer(self.encode_msg_header(resp_msg_type, comp_id, comp_id_s, msg_len,
                                                                 present_map) + msg_body)
        mm += Utils.print_binary(message)
        self.logger.info(mm)
        # message = b'Response ... '
        self.response_created = True
        self._send_buffer += message
        self.request = b''
        self._set_selector_events_mask('r')

    def handle_resend_request(self, present_map, msg_len, comp_id, comp_id_s):
        mm = 'Resend Request='
        self.logger.info('Test Request')
        resp_msg_type = MsgType.SEQUENCE_RESET
        pos = 54
        seqs = struct.unpack('<II', self.request[pos: pos + 8])
        start_seq = seqs[0]
        end_seq = seqs[1]
        self.logger.info('****** resend request: start_seq=%d, end_seq=%d', start_seq, end_seq)
        if end_seq == 0:
            end_seq = start_seq
        # while start_seq <= end_seq:
        msg_len = 58
        present_map[0], present_map[1] = 1, 1
        msg_len += 5
        msg_body = struct.pack('<BI', ord('N'), end_seq)
        message = self.encode_msg_trailer(self.encode_msg_header(resp_msg_type, comp_id, comp_id_s, msg_len,
                                                                 present_map) + msg_body)
        mm += Utils.print_binary(message)
        self.logger.info(mm)
        # message = b'Response ... '
        self.response_created = True
        self._send_buffer += message

        self.request = b''
        self._set_selector_events_mask('r')

    def handle_heartbeat(self, present_map, msg_len, comp_id, comp_id_s):
        mm = 'Heart Beat='
        resp_msg_type = MsgType.HEART_BEAT
        self.logger.info('Heart Beat')
        msg_body = b''
        message = self.encode_msg_trailer(self.encode_msg_header(resp_msg_type, comp_id, comp_id_s, msg_len,
                                                                 present_map) + msg_body)
        mm += Utils.print_binary(message)
        self.logger.info(mm)
        # message = b'Response ... '
        self.response_created = True
        self._send_buffer += message
        self.request = b''
        self._set_selector_events_mask('r')

    def handle_logout(self, present_map, msg_len, comp_id, comp_id_s):
        mm = 'Logout='
        resp_msg_type = MsgType.LOGOUT
        self.logger.info('Logout')
        # Session Status
        present_map[1] = 1
        msg_len += 1
        msg_body = struct.pack('<B', 0)
        message = self.encode_msg_trailer(self.encode_msg_header(resp_msg_type, comp_id, comp_id_s, msg_len,
                                                                 present_map) + msg_body)
        mm += Utils.print_binary(message)
        self.logger.info(mm)
        # message = b'Response ... '
        self.response_created = True
        self._send_buffer += message
        self.request = b''
        self._set_selector_events_mask('r')

    def handle_logon(self, present_map, msg_len, comp_id, comp_id_s):
        mm = 'Logon='
        resp_msg_type = MsgType.LOGON
        self.logger.info('Logon Message')
        seq_num=struct.unpack('<I',self.request[4:8])[0]
        pm = bitarray(format(self.request[22], 'b').zfill(8), endian='big')
        pos = 54
        if pm[0]:
            password = self.request[pos: pos + 450]
            pos += 450
            self.logger.info('password=%s', password.decode('utf-8'))
        if pm[1]:
            new_password = self.request[pos: pos + 450]
            pos += 450
            self.logger.info('new_password=%s', new_password.decode('utf-8'))
        req_next_expected_seq = struct.unpack('<I', self.request[pos: pos + 4])[0]
        self.send_seq_dict[comp_id_s]=req_next_expected_seq-1
        self.logger.info('send sequence = %d, next expected seq=%d', req_next_expected_seq, seq_num+1)
        # Next Expected message sequence
        present_map[2] = 1
        msg_len += 4
        # if comp_id_s in self.receive_exp_next_seq_dict:
        #    next_expected_seq = self.receive_exp_next_seq_dict[comp_id_s]
        # else:
        #    next_expected_seq = 1
        next_expected_seq=seq_num+1
        # Session Status
        present_map[3] = 1
        msg_len += 1
        msg_body = struct.pack('<IB', next_expected_seq, 0)

        message = self.encode_msg_trailer(self.encode_msg_header(resp_msg_type, comp_id, comp_id_s, msg_len,
                                                                 present_map) + msg_body)
        mm += Utils.print_binary(message)
        self.logger.info(mm)
        # message = b'Response ... '
        self.response_created = True
        self._send_buffer += message
        self.request = b''
        self._set_selector_events_mask('r')

    def handle_new_order(self, present_map, msg_len, comp_id, comp_id_s):
        mm = 'Execution Report='
        self.logger.info('New Order Request')
        resp_msg_type = MsgType.EXECUTION_REPORT
        utc_now = datetime.utcnow()
        transact_time = datetime.strftime(utc_now, '%Y%m%d %H:%M:%S.%f')[:-3]
        pm = bitarray(format(self.request[22], 'b').zfill(8), endian='big')
        pm.extend(format(self.request[23], 'b').zfill(8))
        pm.extend(format(self.request[24], 'b').zfill(8))
        pos = 54
        cl_ord_id = self.request[pos: pos + 21]
        pos += 21
        submitting_broker_id = self.request[pos: pos + 12]
        pos += 12
        security_id = self.request[pos: pos + 21]
        pos += 21
        security_id_source = self.request[pos]
        pos += 1
        exch, broker_location_id, price = None, None, None
        if pm[4]:
            exch = self.request[pos: pos + 5]
            pos += 5
        if pm[5]:
            broker_location_id = self.request[pos: pos + 11]
            pos += 11
        ord_transact_time = self.request[pos: pos + 25]
        pos += 25
        side = self.request[pos]
        pos += 1
        ord_type = self.request[pos]
        pos += 1
        if pm[9]:
            price = struct.unpack('<Q', self.request[pos: pos + 8])[0]
            pos += 8
        order_qty = struct.unpack('<Q', self.request[pos: pos + 8])[0]
        pos += 8
        time_in_force, position_effect, order_restriction, max_price_levels = None, None, None, None
        order_capacity, lot_type, text = None, None, None
        if pm[11]:
            time_in_force = self.request[pos]
            pos += 1
        if pm[12]:
            position_effect = self.request[pos]
            pos += 1
        if pm[13]:
            order_restriction = self.request[pos: pos + 21]
            pos += 21
        if pm[14]:
            max_price_levels = self.request[pos]
            pos += 1
        if pm[15]:
            order_capacity = self.request[pos]
            pos += 1
        self.logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~text~~~~~~~~~~~~~~~~~~~~~~')
        if pm[16]:
            self.logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ has text~~~~~~~~~~~~~~~~~~~~~~')
            text_len = struct.unpack('<H', self.request[pos: pos + 2])[0]
            pos += 2
            text = self.request[pos: pos + text_len]
            pos += text_len
            self.logger.info('text = %s', text)
        if pm[17]:
            exec_inst = self.request[pos: pos + 21]
            pos += 21
        else:
            exec_inst = b''
        if pm[18]:
            disclosure_inst = struct.unpack('<H', self.request[pos: pos + 2])
            pos += 2
        if pm[19]:
            lot_type = self.request[pos]
        self.logger.info('NewOrderSingle[cl_ord_id=%s, security_id=%s, transact_time=%s, side=%d, ord_type=%d'
                         ', order_qty=%d, exec_inst=%s]',
                         cl_ord_id.decode('utf-8'), security_id.decode('utf-8'), ord_transact_time.decode('utf-8')
                         , side, ord_type, order_qty, exec_inst)
        # generate the execution report
        present_map[0], present_map[1], present_map[2], present_map[3], present_map[4] = 1, 1, 1, 1, 1
        msg_body = struct.pack('<21s12s21sB5s', cl_ord_id, submitting_broker_id, security_id, security_id_source,
                               exch)
        msg_len += 21 + 12 + 21 + 1 + 5
        if broker_location_id:
            present_map[5] = 1
            msg_body += struct.pack('<11s', broker_location_id)
            msg_len += 11
        present_map[6], present_map[7], present_map[9], present_map[11] = 1, 1, 1, 1
        order_id = datetime.now().strftime('%H%M%S') + format(str(self.order_seq_no), 's').zfill(5)
        self.clordid_orderid[cl_ord_id] = order_id, order_qty, broker_location_id
        self.order_seq_no += 1
        msg_body += struct.pack('<25sB21sB', transact_time.encode('utf-8'), side, order_id.encode('utf-8')
                                , ord_type)
        msg_len += 25 + 1 + 21 + 1
        if price:
            present_map[12] = 1
            msg_body += struct.pack('<Q', price)
            msg_len += 8
        present_map[13] = 1
        msg_body += struct.pack('<Q', order_qty)
        msg_len += 8
        if time_in_force:
            present_map[14] = 1
            msg_body += struct.pack('<B', time_in_force)
            msg_len += 1
        if position_effect:
            present_map[15] = 1
            msg_body += struct.pack('<B', position_effect)
            msg_len += 1
        if order_restriction:
            present_map[16] = 1
            msg_body += struct.pack('<21s', order_restriction)
            msg_len += 21
        if max_price_levels:
            present_map[17] = 1
            msg_body += struct.pack('<B', max_price_levels)
            msg_len += 1
        if order_capacity:
            present_map[18] = 1
            msg_body += struct.pack('<B', order_capacity)
            msg_len += 1
        if text:
            present_map[19] = 1
            msg_body += struct.pack('<H'+str(len(text)+1)+'s', len(text)+1, text)
            msg_len += len(text)+3
        present_map[21], present_map[22], present_map[23], present_map[24], present_map[25] = 1, 1, 1, 1, 1
        exec_id = datetime.now().strftime('%H%M%S') + format(str(self.exec_id_seq_no), 's').zfill(5)
        self.exec_id_seq_no += 1
        msg_body += struct.pack('<21sBcQQ', exec_id.encode('utf-8'), OrdStatus.NEW,
                                ExecType.NEW.value.encode('utf-8'), 0, order_qty)
        msg_len += 21 + 1 + 1 + 8 + 8
        if lot_type:
            present_map[27] = 1
            msg_body += struct.pack('<B', lot_type)
            msg_len += 1

        message = self.encode_msg_trailer(self.encode_msg_header(resp_msg_type, comp_id, comp_id_s, msg_len,
                                                                 present_map) + msg_body)
        mm += Utils.print_binary(message)
        self.logger.info(mm)
        # message = b'Response ... '
        sleep(1)
        self.response_created = True
        self._send_buffer += message
        try:
            last_px = price
            if not last_px:
                last_px = 100000000
            if 10000000000 < order_qty <= 100000000000:
                self._send_buffer += self.generate_trade(comp_id, comp_id_s, cl_ord_id, submitting_broker_id
                                                         , security_id, side, order_id, ord_type, price, order_qty,
                                                         time_in_force, position_effect, order_qty, order_qty, last_px
                                                         , text, broker_location_id)
            elif 100000000000 < order_qty <= 200000000000:
                last_qty = 100000000000
                cum_qty = last_qty
                self._send_buffer += self.generate_trade(comp_id, comp_id_s, cl_ord_id, submitting_broker_id
                                                         , security_id, side, order_id, ord_type, price, order_qty,
                                                         time_in_force, position_effect, cum_qty, last_qty
                                                         , last_px, text, broker_location_id)
                last_qty = order_qty-last_qty
                self._send_buffer += self.generate_trade(comp_id, comp_id_s, cl_ord_id, submitting_broker_id
                                                         , security_id, side, order_id, ord_type, price, order_qty,
                                                         time_in_force, position_effect, order_qty, last_qty, last_px
                                                         , text, broker_location_id)
            elif 200000000000 < order_qty <= 500000000000:
                last_qty = 50000000000
                cum_qty = last_qty
                self._send_buffer += self.generate_trade(comp_id, comp_id_s, cl_ord_id, submitting_broker_id
                                                         , security_id, side, order_id, ord_type, price, order_qty,
                                                         time_in_force, position_effect, cum_qty, last_qty, last_px
                                                         , text, broker_location_id)
                last_qty = 100000000000
                cum_qty = cum_qty + last_qty
                self._send_buffer += self.generate_trade(comp_id, comp_id_s, cl_ord_id, submitting_broker_id
                                                         , security_id, side, order_id, ord_type, price, order_qty,
                                                         time_in_force, position_effect, cum_qty, last_qty
                                                         , last_px, text, broker_location_id)
                last_qty = order_qty - cum_qty
                self._send_buffer += self.generate_trade(comp_id, comp_id_s, cl_ord_id, submitting_broker_id
                                                         , security_id, side, order_id, ord_type, price, order_qty,
                                                         time_in_force, position_effect, order_qty, last_qty, last_px
                                                         , text, broker_location_id)
            else:
                last_qty = order_qty//2
                cum_qty = last_qty
                self._send_buffer += self.generate_trade(comp_id, comp_id_s, cl_ord_id, submitting_broker_id
                                                         , security_id, side, order_id, ord_type, price, order_qty,
                                                         time_in_force, position_effect, cum_qty, last_qty, last_px
                                                         , text, broker_location_id)
        except Exception:
            self.logger.exception('Some exceptions during executing the crossing')
        finally:
            self.request = b''
            self._set_selector_events_mask('r')

    def generate_trade(self, comp_id, comp_id_s, cl_ord_id, submitting_broker_id, security_id, side, order_id
                       , ord_type, price, order_qty, time_in_force, position_effect, cum_qty, last_qty, last_px, text
                       , broker_location_id):
        present_map = bitarray(32 * 8, endian='big')
        present_map.setall(False)
        resp_msg_type = MsgType.EXECUTION_REPORT
        mm = 'Trade'
        msg_len = 58
        utc_now = datetime.utcnow()
        transact_time = datetime.strftime(utc_now, '%Y%m%d %H:%M:%S.%f')[:-3]
        ord_status = OrdStatus.NEW
        if cum_qty > 0:
            if cum_qty == order_qty:
                ord_status = OrdStatus.FILLED
            else:
                ord_status = OrdStatus.PARTIALLY_FILLED
        # generate the execution report
        present_map[0], present_map[1], present_map[2], present_map[3], present_map[4] = 1, 1, 1, 1, 1
        msg_body = struct.pack('<21s12s21sB5s', cl_ord_id, submitting_broker_id, security_id, 8,
                               'XHKG'.encode('utf-8'))
        msg_len += 21 + 12 + 21 + 1 + 5

        if broker_location_id:
            present_map[5] = 1
            msg_body += struct.pack('<11s', broker_location_id)
            msg_len += 11

        present_map[6], present_map[7], present_map[9], present_map[11] = 1, 1, 1, 1
        msg_body += struct.pack('<25sB21sB', transact_time.encode('utf-8'), side, order_id.encode('utf-8')
                                , ord_type)
        msg_len += 25 + 1 + 21 + 1

        if price:
            present_map[12] = 1
            msg_body += struct.pack('<Q', price)
            msg_len += 8
        present_map[13] = 1
        msg_body += struct.pack('<Q', order_qty)
        msg_len += 8
        if time_in_force:
            present_map[14] = 1
            msg_body += struct.pack('<B', time_in_force)
            msg_len += 1
        if position_effect:
            present_map[15] = 1
            msg_body += struct.pack('<B', position_effect)
            msg_len += 1
        if text:
            present_map[19] = 1
            msg_body += struct.pack('<H'+str(len(text)+1)+'s', len(text)+1, text)
            msg_len += len(text)+3
        present_map[21], present_map[22], present_map[23], present_map[24], present_map[25] = 1, 1, 1, 1, 1
        exec_id = datetime.now().strftime('%H%M%S') + format(str(self.exec_id_seq_no), 's').zfill(5)
        self.exec_id_seq_no += 1
        leaves_qty = order_qty-cum_qty
        msg_body += struct.pack('<21sBcQQ', exec_id.encode('utf-8'), ord_status,
                                ExecType.TRADE.value.encode('utf-8'), cum_qty, leaves_qty)
        msg_len += 21 + 1 + 1 + 8 + 8
        # Execution Quantity and Execution Price

        present_map[31], present_map[32], present_map[33] = 1, 1, 1
        msg_body += struct.pack('<12sQQ', '8888'.encode('utf-8'), last_qty, last_px)
        msg_len += 8 + 8 + 12
        message = self.encode_msg_trailer(self.encode_msg_header(resp_msg_type, comp_id, comp_id_s, msg_len,
                                                                 present_map) + msg_body)
        mm += Utils.print_binary(message)
        self.logger.info(mm)
        return message
