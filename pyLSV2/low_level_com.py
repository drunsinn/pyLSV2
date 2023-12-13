#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""low level communication functions for LSV2"""
import logging
import socket
import struct
from typing import Union

from .const import CMD, RSP, LSV2StatusCode
from .dat_cls import LSV2Error
from .err import LSV2StateException, LSV2ProtocolException


class LSV2TCP:
    """Implementation of the low level communication functions for sending and
    receiving LSV2 telegrams via TCP"""

    DEFAULT_PORT = 19000
    # Default port for LSV2 on control side

    DEFAULT_BUFFER_SIZE = 256
    # Default size of send and receive buffer

    def __init__(self, hostname: str, port: int = 19000, timeout: float = 15.0):
        """Set connection parameters

        :param hostname: ip or hostname of control.
        :param port: port number, defaults to 19000.
        :param timeout: number of seconds for time out of connection.

        :raises socket.gaierror: Hostname could not be resolved
        :raises socket.error: could not create socket
        """
        self._logger = logging.getLogger("LSV2 TCP")

        try:
            self._host_ip = socket.gethostbyname(hostname)
        except socket.gaierror:
            logging.error("there was an error getting the IP for the hostname %s", hostname)
            raise

        self._port = self.DEFAULT_PORT
        if port > 0:
            self._port = port

        self.buffer_size = LSV2TCP.DEFAULT_BUFFER_SIZE

        try:
            self._tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._tcpsock.settimeout(timeout)
        except socket.error as err:
            self._logger.error("socket creation failed with error %s", err)
            raise

        self._is_connected = False
        self._last_lsv2_response = RSP.NONE
        self._last_error = LSV2Error()

        self._logger.debug(
            "Socket successfully created, host %s was resolved to IP %s",
            hostname,
            self._host_ip,
        )

    @property
    def last_response(self) -> RSP:
        """get the response to the last telegram"""
        return self._last_lsv2_response

    @property
    def last_error(self) -> LSV2Error:
        """get the error if the last telegram failed"""
        return self._last_error

    @property
    def buffer_size(self) -> int:
        """size of the buffer used for sending and receiving data.
        has to be negotiated with the control"""
        return self._buffer_size

    @buffer_size.setter
    def buffer_size(self, value: int):
        if value < 8:
            self._buffer_size = self.DEFAULT_BUFFER_SIZE
            self._logger.warning(
                "size of receive buffer to small, set to default of %d bytes",
                self._buffer_size,
            )
        else:
            self._buffer_size = value

    def connect(self):
        """
        Establish connection to control

        :raise socket.timeout: Exception if connection times out.
        """
        try:
            self._tcpsock.connect((self._host_ip, self._port))
        except socket.timeout:
            self._logger.error(
                "could not connect to address '%s' on port %d",
                self._host_ip,
                self._port,
            )
            raise
        except ConnectionRefusedError:
            self._logger.error(
                "connection to address '%s' on port %d was refused",
                self._host_ip,
                self._port,
            )
            raise

        self._is_connected = True
        self._last_lsv2_response = RSP.NONE
        self._last_error = LSV2Error()

        self._logger.debug("Connected to host %s at port %s", self._host_ip, self._port)

    def disconnect(self):
        """
        Close connection

        :raise socket.timeout: Exception if connection times out.
        """
        try:
            if self._tcpsock is not None:
                self._tcpsock.close()
        except socket.timeout:
            self._logger.error("error while closing socket")
            raise

        self._is_connected = False
        self._last_lsv2_response = RSP.NONE
        self._last_error = LSV2Error()

        self._logger.debug("Connection to %s closed", self._host_ip)

    def telegram(
        self,
        command: Union[CMD, RSP],
        payload: bytearray = bytearray(),
        wait_for_response: bool = True,
    ) -> bytearray:
        """
        Send LSV2 telegram and receive response if necessary.

        :param command: command string
        :param payload: command payload
        :param wait_for_response: switch for waiting for response from control.
        :raise LSV2StateException: if connection is not already open or error during transmission.
        :raise OverflowError: if payload is to long for current buffer size
        :raise LSV2ProtocolException: if the reviced response is too short for a minimal telegram
        :raise Exception:
        """
        if self._is_connected is False:
            raise LSV2StateException("connection is not open!")

        if payload is None or len(payload) == 0:
            payload = bytearray()
            payload_length = 0
        else:
            payload_length = len(payload)

        self._last_lsv2_response = RSP.NONE

        telegram = bytearray()
        # L -> unsigned long -> 32 bit
        telegram.extend(struct.pack("!L", payload_length))
        telegram.extend(map(ord, command))

        if len(payload) > 0:
            telegram.extend(payload)
        self._logger.debug(
            "telegram to transmit: command %s payload length %d bytes data: %s",
            command,
            payload_length,
            telegram,
        )
        if len(telegram) >= self.buffer_size:
            raise OverflowError("telegram to long for set current buffer size: %d >= %d" % (len(telegram), self.buffer_size))

        data_recived = bytearray()
        try:
            # send bytes to control
            self._tcpsock.send(bytes(telegram))
            if wait_for_response:
                data_recived = self._tcpsock.recv(self.buffer_size)
        except Exception:
            self._logger.error(
                "something went wrong while waiting for new data to arrive, buffer was set to %d",
                self.buffer_size,
            )
            raise

        if len(data_recived) > 0:
            self._logger.debug("received block of data with length %d", len(data_recived))
            if len(data_recived) >= 8:
                # read 4 bytes for response length
                response_length = struct.unpack("!L", data_recived[0:4])[0]

                # read 4 bytes for response type
                self._last_lsv2_response = RSP(data_recived[4:8].decode("utf-8", "ignore"))
            else:
                # response is less than 8 bytes long which is not enough space for package length and response message!
                raise LSV2ProtocolException("response to short, less than 8 bytes: %s" % data_recived)
        else:
            response_length = 0
            self._last_lsv2_response = RSP.NONE

        if response_length > 0:
            response_content = bytearray(data_recived[8:])
            while len(response_content) < response_length:
                self._logger.debug(
                    "waiting for more data to arrive, %d bytes missing",
                    len(response_content) < response_length,
                )
                try:
                    response_content.extend(self._tcpsock.recv(response_length - len(data_recived[8:])))
                except Exception:
                    self._logger.error(
                        "something went wrong while waiting for more data to arrive. expected %d, received %d, content so far: %s",
                        response_length,
                        len(data_recived),
                        data_recived,
                    )
                    raise
        else:
            response_content = bytearray()

        self._last_error = LSV2Error()
        if self._last_lsv2_response in [RSP.T_ER, RSP.T_BD]:
            if len(response_content) == 2:
                self._last_error = LSV2Error.from_ba(response_content)
            elif len(response_content) == 0:
                self._last_error.e_type = 1
            else:
                raise Exception(response_content)

        return response_content


class LSV2RS232:
    """placeholder implementation of the low level communication functions for sending and
    receiving LSV2 telegrams via RS232"""

    DEFAULT_BUFFER_SIZE = 256
    # Default size of send and receive buffer

    def __init__(self, port: str, speed: int, timeout: float = 15.0):
        self._logger = logging.getLogger("LSV2 RS232")
        self.buffer_size = LSV2RS232.DEFAULT_BUFFER_SIZE

        self._is_connected = False
        self._last_lsv2_response = RSP.NONE
        self._last_error = LSV2Error()
        raise NotImplementedError()
        # import serial

    @property
    def last_response(self) -> RSP:
        """get the response to the last telegram"""
        return self._last_lsv2_response

    @property
    def last_error(self) -> LSV2Error:
        """get the error if the last telegram failed"""
        return self._last_error

    @property
    def buffer_size(self) -> int:
        """size of the buffer used for sending and receiving data.
        has to be negotiated with the control"""
        return self._buffer_size

    @buffer_size.setter
    def buffer_size(self, value: int):
        if value < 8:
            self._buffer_size = self.DEFAULT_BUFFER_SIZE
            self._logger.warning(
                "size of receive buffer to small, set to default of %d bytes",
                self._buffer_size,
            )
        else:
            self._buffer_size = value

    def connect(self):
        """
        Establish connection to control
        """
        raise NotImplementedError()

    def disconnect(self):
        """
        Close connection
        """
        raise NotImplementedError()

    def telegram(
        self,
        command: Union[CMD, RSP],
        payload: bytearray = bytearray(),
        wait_for_response: bool = True,
    ) -> bytearray:
        """
        Send LSV2 telegram and receive response if necessary.

        :param command: command string
        :param payload: command payload
        :param wait_for_response: switch for waiting for response from control.
        """
        raise NotImplementedError()
