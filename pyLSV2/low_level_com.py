#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""low level communication functions for LSV2"""
import logging
import socket
import struct
from .const import RSP

logging.getLogger(__name__).addHandler(logging.NullHandler())


class LLLSV2Com:
    """Implementation of the low level communication functions for sending and
    receiving LSV2 telegrams via TCP"""

    DEFAULT_PORT = 19000  # Default port for LSV2 on control side
    DEFAULT_BUFFER_SIZE = 256

    def __init__(self, hostname: str, port: int = 19000, timeout: float = 15.0):
        """Set connection parameters

        :param str hostname: ip or hostname of control.
        :param int port: port number, defaults to 19000.
        :param float timeout: number of seconds for time out of connection.
        """
        try:
            self._host_ip = socket.gethostbyname(hostname)
        except socket.gaierror:
            logging.error("there was an error resolving the host")
            raise

        self._port = self.DEFAULT_PORT
        if port > 0:
            self._port = port

        self._buffer_size = -1
        self.set_buffer_size(LLLSV2Com.DEFAULT_BUFFER_SIZE)

        try:
            self._tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._tcpsock.settimeout(timeout)
        except socket.error as err:
            logging.error("socket creation failed with error %s", err)
            raise
        self._is_connected = False

        logging.debug(
            "Socket successfully created, host %s was resolved to IP %s",
            hostname,
            self._host_ip,
        )

    def connect(self):
        """Establish connection to control

        :raise: Exception if connection times out.
        :rtype: None
        """
        try:
            self._tcpsock.connect((self._host_ip, self._port))
        except socket.timeout:
            logging.error("could not connect to control")
            raise
        self._is_connected = True
        logging.debug("Connected to host %s at port %s", self._host_ip, self._port)

    def disconnect(self):
        """Close connection

        :raise: Exception if connection times out.
        :rtype: None
        """
        try:
            if self._tcpsock is not None:
                self._tcpsock.close()
        except socket.timeout:
            logging.error("error while closing socket")
            raise
        self._is_connected = False
        logging.debug("Connection to %s closed", self._host_ip)

    def set_buffer_size(self, buffer_size: int) -> bool:
        """set the size of the send and recive buffer. the size has to be established during connection setup.
        buffer size has to be at least 8 so command and lenght fit into the telegram"""
        if buffer_size < 8:
            self._buffer_size = self.DEFAULT_BUFFER_SIZE
            logging.warning(
                "size of receive buffer to small, set to default of %d bytes",
                self._buffer_size,
            )
            return False
        self._buffer_size = buffer_size
        return True

    def get_buffer_size(self) -> int:
        """return current send/recive buffer size"""
        return self._buffer_size

    def telegram(self, command, payload: bytearray = bytearray(), wait_for_response: bool = True):
        """Send LSV2 telegram and receive response if necessary.

        :param str command: command string.
        :param byte array payload: command payload.
        :param bool wait_for_response: switch for waiting for response from control.
        :raise: Exception if connection is not already open or error during transmission.
        :return: response message and content
        :rtype: list
        """
        if self._is_connected is False:
            raise Exception("connection is not open!")

        if payload is None or len(payload) == 0:
            payload = bytearray()
            payload_length = 0
        else:
            payload_length = len(payload)

        telegram = bytearray()
        # L -> unsigned long -> 32 bit
        telegram.extend(struct.pack("!L", payload_length))
        telegram.extend(map(ord, command))

        if len(payload) > 0:
            telegram.extend(payload)
        logging.debug(
            "telegram to transmit: command %s payload length %d bytes data: %s",
            command,
            payload_length,
            telegram,
        )
        if len(telegram) >= self._buffer_size:
            raise OverflowError(
                "telegram to long for set current buffer size: %d >= %d"
                % (len(telegram), self._buffer_size)
            )

        response = bytearray()
        try:
            self._tcpsock.send(bytes(telegram))
            if wait_for_response:
                response = self._tcpsock.recv(self._buffer_size)
        except Exception:
            logging.error(
                "something went wrong while waiting for new data to arrive, buffer was set to %d",
                self._buffer_size,
            )
            raise

        if len(response) > 0:
            logging.debug("recived block of data with lenght %d", len(response))
            if len(response) >= 8:
                # read 4 bytes for response length
                response_length = struct.unpack("!L", response[0:4])[0]

                # read 4 bytes for response type
                response_command = RSP(response[4:8].decode("utf-8", "ignore"))
            else:
                # respons is less than 8 bytes long which is not enough space for package lengh and response message!
                raise Exception("response to short, less than 8 bytes: %s" % response)
        else:
            response_length = 0
            response_command = RSP.NONE

        if response_length > 0:
            response_content = bytearray(response[8:])
            while len(response_content) < response_length:
                logging.debug(
                    "waiting for more data to arrive, %d bytes missing",
                    len(response_content) < response_length,
                )
                try:
                    response_content.extend(
                        self._tcpsock.recv(response_length - len(response[8:]))
                    )
                except Exception:
                    logging.error(
                        "something went wrong while waiting for more data to arrive"
                    )
                    raise
        else:
            response_content = None

        return response_command, response_content
