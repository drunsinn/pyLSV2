#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import struct
import logging
import socket

class LLLSV2Com(object):
    DEFAULT_PORT = 19000 # Default port for LSV2 on control side
    DEFAULT_BUFFER_SIZE = 256 # in the eclipse plugin it is set to 256-10, why ?

    def __init__(self, hostname, port=0, timeout=15.0):
        try:
            self._host_ip = socket.gethostbyname(hostname)
        except socket.gaierror:
            logging.error('there was An error resolving the host')
            raise

        if port == 0:
            self._port = LLLSV2Com.DEFAULT_PORT
            logging.warning('port number was not set, changing it to default')
        else:
            self._port = port

        try:
            self._tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._tcpsock.settimeout(timeout)
        except socket.error as err:
            logging.error('socket creation failed with error {}'.format(err))
            raise
        self._is_connected = False
        self._last_error_message = ''
        logging.debug('Socket successfully created, host {} was resolved to IP {}'.format(hostname, self._host_ip))

    def connect(self):
        """connect to control"""
        try:
            self._tcpsock.connect((self._host_ip, self._port))
        except socket.timeout:
            logging.error('could not connect to control')
            raise
        self._is_connected = True
        logging.debug('Connected to host {} at port {}'.format(self._host_ip, self._port))

    def disconnect(self):
        """logout of all open logins and close connection"""
        try:
            self._tcpsock.close()
        except socket.timeout:
            logging.error('error while closing socket')
            raise
        self._is_connected = False
        logging.debug('Connection to {} closed'.format(self._host_ip))

    def telegram(self, command, payload=None, buffer_size=0):
        """this function handles sending telegrams to the control"""
        if self._is_connected is False:
            raise Exception('connection is not open!')

        if payload is None:
            payload_length = 0
        else:
            payload_length = len(payload)

        if buffer_size < 8:
            buffer_size = LLLSV2Com.DEFAULT_BUFFER_SIZE
            logging.warning('size of receive buffer to small, set to default of {} bytes'.format(LLLSV2Com.DEFAULT_BUFFER_SIZE))

        telegram = bytearray()
        telegram.extend(struct.pack('!L', payload_length)) # L -> unsigned long -> 32 bit
        telegram.extend(map(ord, command))
        if payload is not None:
            telegram.extend(payload)
        logging.debug('telegram to transmit: command {} payload length {} bytes'.format(command, payload_length))
        if len(telegram) >= buffer_size:
            raise OverflowError('telegram to long for set current buffer size: {} >= {}'.format(len(telegram), buffer_sizee))

        try:
            self._tcpsock.send(telegram)
            response = self._tcpsock.recv(buffer_size) # get first 8 bytes: length + response
        except:
            raise

        response_length = struct.unpack('!L', response[0:4])[0] # read 4 bytes for response length
        response_command = response[4:8].decode('utf-8', 'ignore') # read 4 bytes for response type
        logging.debug('response telegram {} with overall length of {} bytes, actual length including header is {}'.format(response_command, response_length, len(response)))

        if len(response) > 8:
            response_content = response[8:]
        else:
            response_content = None

        return response_command, response_content
