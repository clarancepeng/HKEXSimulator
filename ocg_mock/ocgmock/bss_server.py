"""
    HKEX Simulation
    Socket communication
"""
import os
import sys
import selectors
import socket
import yaml
import logging
from ocgmock import message_handle

sel = selectors.DefaultSelector()
keep_running = True


def init_logger():
    log_format = '%(asctime)-15s %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=log_format)
    # , format='%(asctime)s - %(name)% - %(levelname)s - %(message)s')
    logger_l = logging.getLogger(__name__)
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.DEBUG)
    f_handler = logging.FileHandler('bss_server.log')
    f_handler.setLevel(logging.INFO)
    c_format = logging.Formatter(log_format)
    f_format = logging.Formatter(log_format)
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)
    # logger_l.addHandler(c_handler)
    logger_l.addHandler(f_handler)
    return logger_l


def accept_wrapper(sock, logger2, config_map):
    conn, addr = sock.accept()
    logger2.info('accepted connection from %s', addr)
    conn.setblocking(False)
    msg = message_handle.Message(sel, conn, addr, keep_running, logger2, config_map)
    sel.register(conn, selectors.EVENT_READ, data=msg)


if __name__ == '__main__':
    logger = init_logger()
    try:
        with open(os.getcwd() + "/../config/lookup-cfg.yaml", 'r') as stream:
            try:
                d = yaml.safe_load(stream)
                print(d)
            except yaml.YAMLError as exc:
                logger.exception('Could not handle the configuration file!')
                sys.exit(0)
    except FileNotFoundError as exc:
        with open(os.getcwd() + "/config/lookup-cfg.yaml", 'r') as stream:
            try:
                d = yaml.safe_load(stream)
                print(d)
            except yaml.YAMLError as exc:
                logger.exception('Could not handle the configuration file!')
                sys.exit(0)
    logger.info('primary[ip=%s, port= %d]', d['primary']['ip'], d['primary']['port'])

    if len(sys.argv) != 3:
        logger.info("usage: %s <host> <port>", sys.argv[0])
        sys.exit(1)
    host, port = sys.argv[1], int(sys.argv[2])
    '''
    host, port = d['primary']['ip'], int(d['primary']['port'])
    '''
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lsock.bind((host, port))
    lsock.listen()
    logger.info('listening on %s', (host, port))
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)

    try:
        while keep_running:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj, logger, None)
                else:
                    message = key.data
                    try:
                        message.process_events(mask)
                    except Exception:
                        logger.exception('main: error: exception for %s', message.addr)
                        message.close()
    except KeyboardInterrupt:
        logger.exception('caught keyboard interrupt, exiting')
    finally:
        sel.close()

