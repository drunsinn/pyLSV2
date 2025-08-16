#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""low level communication functions for LSV2"""

import logging
import socket
import struct
from typing import Union

from .const import CMD, RSP, BYTE_STX, BYTE_ETX, BYTE_EOT, BYTE_DLE, BYTE_ENQ, BYTE_ACK, BYTE_NAK
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

    def __init__(self, port: str, speed: int, timeout: float = 1.0):
        self._logger = logging.getLogger("LSV2 RS232")
        self.buffer_size = LSV2RS232.DEFAULT_BUFFER_SIZE

        import serial

        try:
            self._rs232 = serial.Serial(port=port, baudrate=speed, timeout=timeout)
            self._rs232.bytesize = serial.EIGHTBITS
            self._rs232.parity = serial.PARITY_NONE
            self._rs232.stopbits = serial.STOPBITS_ONE
            self._rs232.xonxoff = False  # disable software flow control
            self._rs232.rtscts = False  # disable hardware flow control
            self._rs232.dsrdtr = False  # disable hardware flow control
            self._rs232.timeout = timeout
            self._rs232.write_timeout = self.buffer_size

        except serial.SerialException as err:
            self._logger.error("serial port creation failed with error %s", err)
            raise

        self._last_lsv2_response = RSP.NONE
        self._last_error = LSV2Error()

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
        try:
            self._rs232.open()
        except serial.SerialException as err:
            self._logger.error("could not open serial port: %s", err)
            raise

        self._last_lsv2_response = RSP.NONE
        self._last_error = LSV2Error()

        self._logger.debug("Connected to serial port %s", self._rs232.port)

    def disconnect(self):
        """
        Close connection
        """
        if self._rs232 is not None:
            self._rs232.close()

        self._last_lsv2_response = RSP.NONE
        self._last_error = LSV2Error()

        self._logger.debug("Connection to %s closed", self._rs232.port)

    @staticmethod
    def calculate_bcc(payload: bytearray):
        """helper function to calculate the block check character
        - taken from github project Sistema-Flexivel-Heidenhain
        """
        result = 0
        for character in payload:
            if character not in [int.from_bytes(BYTE_DLE), int.from_bytes(BYTE_STX)]:
                # dont include <DLE> and <STX> in checksum
                result ^= character
        # result ^= 3 # Why???? # not sure what this was supposed to do......
        return result

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

        if self._rs232.is_open is False:
            raise LSV2StateException("connection is not open!")

        retry_counter = 0
        while retry_counter < 3:
            self.__rest_phase()
            if self.__request_phase() is False:
                if self.__transfer_phase(command, payload) is False:
                    break
            
            retry_counter += 1
        if retry_counter >= 3:
            self._logger.error("could not send telegram after 3 retries, returning to rest phase")
            self.__rest_phase()
            raise LSV2StateException("could not send telegram after 3 retries")

    def __rest_phase(self):
        """
        rest phase of transfer, nothing is sent or received
        reset everything
        """
        self._rs232.reset_input_buffer()
        self._rs232.reset_output_buffer()

    def __request_phase(self):
        """
        request phase
        send <ENQ> to control
        read response
        """
        stat = self._rs232.write(BYTE_ENQ)
        if stat != 1:
            self._logger.error("could not send <ENQ> to control")
            raise LSV2StateException("could not send <ENQ> to control")

        # wait/read for response
        ## send <ENQ>  and receive response
        ## <DLE><0> control is ready -> start transfer phase
        ## <NAK> control is not ready -> send <EOT> and return to rest phase
        ## <DLE><1> control is still busy with transfer -> send <EOT> and return to rest phase
        ## <ENQ> control also wants to send data -> postpone transmission, acknowledge receive with <DLE><0> and receive data. Only after receive is finished, retry send
        ## X X X any other text is ignored, retry for (duration1), if no valid response is received, return to rest phase

        response = self._rs232.read(self._buffer_size)
        if len(response) == 0:
            self._logger.error("serial connection timed out, no response received")
            raise LSV2StateException("serial connection timed out, no response received")
        elif len(response) == 1:
            if response[0] == BYTE_NAK:
                # control is not ready -> send <EOT> and return to rest phase
                self._logger.debug("control is not ready, sending <EOT> and returning to rest phase")
                self._rs232.write(BYTE_EOT)
                return False
            elif response[0] == BYTE_ENQ:
                # control also wants to send data -> postpone transmission, acknowledge receive with <DLE><0> and receive data. Only after receive is finished, retry send
                self._logger.debug("control also wants to send data, acknowledging with <DLE><0>")
                payload = bytearray()
                payload.extend(BYTE_DLE)
                payload.extend(bytes([0x30]))  # <0> for acknowledge
                stat = self._rs232.write(payload)
                if stat != 2:
                    self._logger.error("could not send <DLE><0> to control")
                    raise LSV2StateException("could not send <DLE><0> to control")
                return False
            else:
                raise LSV2ProtocolException("unexpected response received: %s" % response)
        elif len(response) == 2:
            if response[0] == BYTE_DLE:
                if response[1] == 0x30:
                    # control is ready -> start transfer phase
                    raise NotImplementedError()
                elif response[1] == 0x31:
                    # control is still busy with transfer -> send <EOT> and return to rest phase
                    raise NotImplementedError()
                else:
                    raise LSV2ProtocolException("unexpected response received: %s" % response)
            else:
                raise LSV2ProtocolException("unexpected response received: %s" % response)
        else:
            # any other text is ignored, retry for (duration1), if no valid response is received, return to rest phase
            raise LSV2StateException("")
        return True

    def __transfer_phase(
        self,
        command: Union[CMD, RSP],
        payload: bytearray = bytearray(),
    ):
        """
        Transfer phase:
        send <DLE><STX>Telegram<DLE><ETX>BCC
            BCC = calculate_bcc(<DLE><STX>Telegram<DLE><ETX>)
        receive
            - <ACK> control acknowledges received telegram, as well as a correct BCC
            - 3*<NAK> control is not ready, send <EOT> and return to rest phase
            - X X X any other text is ignored, retry for (duration2), if no valid response is received, return to rest pahse
            - nothing if nothing is received for (duration1), return to request phase. If this happens three times in a row, send <EOT> and return to rest phase
        send <EOT> to notify control about successful transmission, return to rest phase
        """

        data = bytearray()
        data.extend(BYTE_DLE)
        data.extend(BYTE_STX)
        data.extend(map(ord, command))
        if len(payload) > 0:
            data.extend(payload)
        data.extend(BYTE_DLE)
        data.extend(BYTE_ETX)
        bcc = self.calculate_bcc(data)
        data.extend(bcc)

        # send
        stat = self._rs232.write(data)
        if stat != 1:
            self._logger.error("could not send <ENQ> to control")
            raise LSV2StateException("could not send <ENQ> to control")

        # receive
        response = self._rs232.read(self._buffer_size)
        if len(response) == 0:
            # nothing if nothing is received for (duration1), return to request phase. If this happens three times in a row, send <EOT> and return to rest phase
            raise NotImplementedError()
        elif len(response) == 1:
            if response[0] == BYTE_ACK:
                # control acknowledges received telegram, as well as a correct BCC
                raise NotImplementedError()
            else:
                raise LSV2StateException()
        elif len(response) == 3:
            if response == bytearray([BYTE_NAK, BYTE_NAK, BYTE_NAK]):
                # 3*<NAK> control is not ready, send <EOT> and return to rest phase
                raise NotImplementedError()
            else:
                raise LSV2StateException("")
        else:
            # any other text is ignored, retry for (duration1), if no valid response is received, return to rest phase
            raise LSV2StateException("")
