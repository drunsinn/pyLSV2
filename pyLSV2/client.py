#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This library is an attempt to implement the LSV2 communication protocol used by certain
CNC controls.
Please consider the dangers of using this library on a production machine! This library is
by no means complete and could damage the control or cause injuries! Everything beyond simple
file manipulation is blocked by a lockout parameter. Use at your own risk!

TODO: research and implement support for `self._sys_par.turbo_mode_active`
TODO: research and implement support for `self._sys_par.dnc_mode_allowed`
TODO: fix unknown parameter type warnings in scope function `real_time_readings`
TODO: add wrapper for `read_plc_memory` to support addressing with named addresses like W0 or D2
TODO: add serial mode to low level com

"""
import logging
import math
import pathlib
import re
import struct
from datetime import datetime
from types import TracebackType
from typing import List, Union, Optional, Type, Dict
import time

from . import const as lc
from . import dat_cls as ld
from . import misc as lm
from . import misc_scope as lms
from . import translate_messages as lt
from .low_level_com import LSV2TCP
from .err import (
    LSV2DataException,
    LSV2InputException,
    LSV2ProtocolException,
    LSV2StateException,
)


class LSV2:
    """implements functions for communicationg with CNC controls via LSV2"""

    def __init__(self, hostname: str, port: int = 0, timeout: float = 15.0, safe_mode: bool = True, compatibility_mode: bool = False):
        """
        Implementation of the LSV2 protocol used to communicate with certain CNC controls

        :param hostname: hostname or IP address of the controls
        :param port: port number to connect to
        :param timeout: number of seconds waited for a response
        :param safe_mode: switch to disable safety functions that might influence the control
        :param compatibility_mode: switch to connect using the least amount of features, for example the buffer size
        """
        self._logger = logging.getLogger("LSV2 Client")

        self._llcom = LSV2TCP(hostname, port, timeout)

        self._active_logins = []

        self.switch_safe_mode(safe_mode)

        self._versions = ld.VersionInfo()
        self._sys_par = ld.SystemParameters()

        self._secure_file_send = False
        self._comp_mode = compatibility_mode

    @property
    def versions(self) -> ld.VersionInfo:
        """version information of the connected control"""
        return self._versions

    @property
    def parameters(self) -> ld.SystemParameters:
        """system parameters of the connected control"""
        return self._sys_par

    @property
    def last_error(self) -> ld.LSV2Error:
        """type and code of the last transmission error"""
        return self._llcom.last_error

    def connect(self):
        """connect to control"""
        self._llcom.connect()
        self._configure_connection()

    def disconnect(self):
        """logout of all open logins and close connection"""
        self.logout(login=None)

        self._versions = ld.VersionInfo()
        self._sys_par = ld.SystemParameters()

        self._llcom.disconnect()
        self._logger.debug("connection to host closed")

    def __enter__(self):
        """enter context"""
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ):
        """exit context"""
        self._logger.debug(
            "close context with exception type '%s', value '%s' and traceback '%s'",
            exc_type,
            exc_value,
            exc_tb,
        )
        self.disconnect()

    def switch_safe_mode(self, enable_safe_mode: bool = True):
        """switch between safe mode and unrestricted mode"""
        if enable_safe_mode is False:
            self._logger.info("disabling safe mode. login and system commands are not restricted. Use with caution!")
            self._known_logins = tuple(e.value for e in lc.Login)
            self._known_sys_cmd = tuple(e.value for e in lc.ParCCC)
        else:
            self._logger.info("enabling safe mode. restricting functionality")
            self._known_logins = (
                lc.Login.INSPECT,
                lc.Login.FILETRANSFER,
                lc.Login.MONITOR,
            )
            self._known_sys_cmd = (
                lc.ParCCC.SET_BUF1024,
                lc.ParCCC.SET_BUF512,
                lc.ParCCC.SET_BUF2048,
                lc.ParCCC.SET_BUF3072,
                lc.ParCCC.SET_BUF4096,
                lc.ParCCC.SECURE_FILE_SEND,
                lc.ParCCC.SCREENDUMP,
            )

    def _send_recive(
        self,
        command: Union[lc.CMD, lc.RSP],
        payload: Union[bytes, bytearray, None] = None,
        expected_response: lc.RSP = lc.RSP.NONE,
    ) -> Union[bool, bytearray]:
        """
        Takes a command and optional payload, sends it to the control and checks if the next telegram contains the
        expected response. If the correct response is received, returns response content if available, or ``True`` if
        no content was received. Otherwiese returns ``False`` on error.

        Use :py:attr:`~pyLSV2.LSV2.last_error` to check the cause of the last error.

        :param command: valid LSV2 command to send
        :param payload: data to send along with the command
        :param expected_response: expected response telegram from the control to signal success

        :raises LSV2ProtocolException: if an unknown/unexpected response was received
        """

        if payload is None:
            bytes_to_send = bytearray()
        elif isinstance(payload, (bytearray,)):
            bytes_to_send = payload
        else:
            bytes_to_send = bytearray(payload)

        if command is lc.CMD.C_CC:
            if len(bytes_to_send) < 2:
                self._logger.warning("system command requires a payload of at exactly 2 bytes")
                return False

            c_cc_command = struct.unpack("!H", bytes_to_send[0:2])[0]
            if c_cc_command not in self._known_sys_cmd:
                self._logger.debug("unknown or unsupported system command %s", bytes_to_send)
                return False

        wait_for_response = bool(expected_response is not lc.RSP.NONE)
        lsv_content = self._llcom.telegram(command, bytes_to_send, wait_for_response)

        if self._llcom.last_response is lc.RSP.UNKNOWN:
            self._logger.error("unknown response received")
            raise LSV2ProtocolException("unknown response received")

        if self._llcom.last_response is lc.RSP.T_ER:
            if self.last_error.e_code is lc.LSV2StatusCode.T_ER_NO_NEXT_ERROR:
                # workaround since querying for error messages will also return an error state
                return True

            self._logger.info(
                "an error was received after the last transmission, %s '%s'",
                self.last_error,
                lt.get_error_text(self.last_error),
            )
            return False

        if self._llcom.last_response is expected_response:
            # expected response received
            self._logger.debug("expected response received: %s", self._llcom.last_response)
            if len(lsv_content) > 0:
                return lsv_content
            return True

        if expected_response is lc.RSP.NONE:
            self._logger.debug("no response expected")
            return False

        self._logger.info("received unexpected response %s", self._llcom.last_response)
        return False

    def _send_recive_block(
        self,
        command: Union[lc.CMD, lc.RSP],
        payload: bytearray,
        expected_response: lc.RSP = lc.RSP.NONE,
    ) -> Union[bool, List[bytearray]]:
        """
        Takes a command and optional payload, sends it to the control and continues reading telegrams until a
        telegram contains the expected response or an error response. If the correct response is received, returns
        the accumulated response content. Otherwiese returns ``False`` on error.

        Use :py:attr:`~pyLSV2.LSV2.last_error` to check the cause of the last error.

        :param command: valid LSV2 command to send
        :param payload: data to send along with the command
        :param expected_response: expected response telegram from the control to signal success
        """

        bytes_to_send = payload

        lsv_content = self._llcom.telegram(command, bytes_to_send)

        if self._llcom.last_response is lc.RSP.UNKNOWN:
            self._logger.info("unknown response received, abort")
            return False

        if self._llcom.last_response is lc.RSP.T_ER:
            self._logger.warning(
                "error received, %s '%s'",
                self.last_error,
                lt.get_error_text(self.last_error),
            )
            return False

        if self._llcom.last_response in lc.RSP.T_FD:
            if len(lsv_content) > 0:
                self._logger.error(
                    "transfer should have finished without content but data received: %s",
                    lsv_content,
                )
            else:
                self._logger.debug("transfer finished without content")
            return False

        response_buffer: List[bytearray] = []
        if self._llcom.last_response is expected_response:
            # expected response received
            self._logger.debug("expected response received: %s", self._llcom.last_response)
            while self._llcom.last_response is expected_response:
                response_buffer.append(lsv_content)
                lsv_content = self._llcom.telegram(command=lc.RSP.T_OK)
            return response_buffer

        self._logger.info(
            "received unexpected response %s, with data %s",
            self._llcom.last_response,
            lsv_content,
        )
        return False

    def _configure_connection(self):
        """
        Set up the communication parameters for file transfer.
        Buffer size and secure file transfere are enabled based on the capabilitys of the control.
        Automatically enables Login ``INSPECT`` and ``FILETRANSFER``

        :raises LSV2ProtocolException: if buffer size could not be negotiated or setting of buffer
                                       size did not work
        """
        self.login(login=lc.Login.INSPECT)

        self._read_version()

        self._read_parameters()

        self._logger.debug(
            "setting connection settings for %s and block length %s",
            self._versions.type,
            self._sys_par.max_block_length,
        )

        selected_size = -1
        selected_command = None
        if self._sys_par.max_block_length >= 4096:
            selected_size = 4096
            selected_command = lc.ParCCC.SET_BUF4096
        elif 3072 <= self._sys_par.max_block_length < 4096:
            selected_size = 3072
            selected_command = lc.ParCCC.SET_BUF3072
        elif 2048 <= self._sys_par.max_block_length < 3072:
            selected_size = 2048
            selected_command = lc.ParCCC.SET_BUF2048
        elif 1024 <= self._sys_par.max_block_length < 2048:
            selected_size = 1024
            selected_command = lc.ParCCC.SET_BUF1024
        elif 512 <= self._sys_par.max_block_length < 1024:
            selected_size = 512
            selected_command = lc.ParCCC.SET_BUF512
        elif 256 <= self._sys_par.max_block_length < 512:
            selected_size = 256
        else:
            self._logger.error(
                "could not decide on a buffer size for maximum message length of %d",
                self._sys_par.max_block_length,
            )
            raise LSV2ProtocolException("could not negotiate buffer site, unknown buffer size of %d" % self._sys_par.max_block_length)

        if selected_command is None:
            self._logger.debug("use smallest buffer size of 256")
            self._llcom.buffer_size = selected_size
        elif self._comp_mode:
            self._logger.debug("compatibility mode active, use lowest buffer size of 256")
            self._llcom.buffer_size = 256
        else:
            self._logger.debug("use buffer size of %d", selected_size)
            if self._send_recive(lc.CMD.C_CC, struct.pack("!H", selected_command), lc.RSP.T_OK):
                self._llcom.buffer_size = selected_size
            else:
                raise LSV2ProtocolException("error in communication while setting buffer size to %d" % selected_size)

        if self._comp_mode:
            self._logger.debug("compatibility mode active, secure file send is ignored")
            self._secure_file_send = False
        else:
            if not self._send_recive(lc.CMD.C_CC, struct.pack("!H", lc.ParCCC.SECURE_FILE_SEND), lc.RSP.T_OK):
                self._logger.debug("secure file transfer not supported? use fallback")
                self._secure_file_send = False
            else:
                self._logger.debug("secure file send is enabled")
                self._secure_file_send = True

        self.login(login=lc.Login.FILETRANSFER)

        self._logger.info("successfully configured connection parameters and basic logins")

    def login(self, login: lc.Login, password: str = "") -> bool:
        """
        Request additional access rights. To elevate this level a logon has to be performed.
        Some levels require a password.
        Returns ``True`` if execution was successful.

        :param login: One of the known login strings
        :param password: optional. Password for login
        """

        if login in self._active_logins:
            self._logger.debug("login already active")
            return True

        if login not in self._known_logins:
            self._logger.warning("unknown or unsupported login")
            return False

        payload = lm.ustr_to_ba(login.value)

        if len(password) > 0:
            payload.extend(lm.ustr_to_ba(password))

        if self._send_recive(lc.CMD.A_LG, payload, lc.RSP.T_OK):
            self._logger.debug("login executed successfully for login %s", login.value)
            self._active_logins.append(login)
            return True

        self._logger.warning("error logging in as %s", login.value)
        return False

    def logout(self, login: Union[lc.Login, None] = None) -> bool:
        """
        Drop one or all access right. If no login is supplied all active access rights are dropped.
        Returns ``True`` if execution was successful.

        :param login: optional. One of the known login strings
        """
        payload = bytearray()

        if login is not None:
            if login in self._active_logins:
                payload.extend(lm.ustr_to_ba(login.value))
            else:
                # login is not active
                return True

        if self._send_recive(lc.CMD.A_LO, payload, lc.RSP.T_OK):
            self._logger.info("logout executed successfully for login %s", login)
            if login is None:
                self._active_logins: List[lc.Login] = []
            else:
                self._active_logins.remove(login)
            return True
        return False

    def _read_parameters(self, force: bool = False) -> ld.SystemParameters:
        """
        Read all available system parameter entries. The results are buffered since it is also used internally.
        This means additional calls dont cause communication with the control.

        :param force: if ``True`` the information is re-read even if it is already buffered
        """
        if self._sys_par.lsv2_version != -1 and force is False:
            self._logger.debug("system parameters already in memory, return previous values")
        else:
            result = self._send_recive(lc.CMD.R_PR, None, lc.RSP.S_PR)
            if isinstance(result, (bytearray,)):
                self._sys_par = lm.decode_system_parameters(result)
            else:
                self._logger.warning("an error occurred while querying system parameters")

            payload = struct.pack("!L", lc.ParRCI.TURBO_MODE)
            result = self._send_recive(lc.CMD.R_CI, payload, lc.RSP.S_CI)
            if isinstance(result, (bytearray,)) and len(result) > 0:
                data = lm.decode_system_information(result)
                if not isinstance(data, bool):
                    raise LSV2DataException("expected boolean")
                self._sys_par.turbo_mode_active = data
            else:
                self._logger.debug("could not read system information on turbo mode")

            payload = struct.pack("!L", lc.ParRCI.DNC_ALLOWED)
            result = self._send_recive(lc.CMD.R_CI, payload, lc.RSP.S_CI)
            if isinstance(result, (bytearray,)) and len(result) > 0:
                data = lm.decode_system_information(result)
                if not isinstance(data, bool):
                    raise LSV2DataException("expected boolean")
                self._sys_par.dnc_mode_allowed = data
            else:
                self._logger.debug("could not read system information on dnc mode")

            payload = struct.pack("!L", lc.ParRCI.AXES_SAMPLING_RATE)
            result = self._send_recive(lc.CMD.R_CI, payload, lc.RSP.S_CI)
            if isinstance(result, (bytearray,)) and len(result) > 0:
                self._sys_par.axes_sampling_rate = lm.decode_system_information(result)
            else:
                self._logger.debug("could not read system information on axes sampling rate")
        return self._sys_par

    def _read_version(self, force: bool = False) -> ld.VersionInfo:
        """
        Read all available version information entries. The results are buffered since it is also used internally.
        This means additional calls dont cause communication with the control.

        :param force: if ``True`` the information is re-read even if it is already buffered

        :raises LSV2DataException: if basic information could not be read from control
        """
        if len(self._versions.control) > 0 and force is False:
            self._logger.debug("version info already in memory, return previous values")
        else:
            info_data = ld.VersionInfo()

            result = self._send_recive(lc.CMD.R_VR, struct.pack("!B", lc.ParRVR.CONTROL), lc.RSP.S_VR)
            if isinstance(result, (bytearray,)) and len(result) > 0:
                info_data.control = lm.ba_to_ustr(result)
            else:
                raise LSV2DataException("Could not read version information from control")

            result = self._send_recive(
                lc.CMD.R_VR,
                struct.pack("!B", lc.ParRVR.NC_VERSION),
                lc.RSP.S_VR,
            )
            if isinstance(result, (bytearray,)) and len(result) > 0:
                info_data.nc_sw = lm.ba_to_ustr(result)

            result = self._send_recive(
                lc.CMD.R_VR,
                struct.pack("!B", lc.ParRVR.PLC_VERSION),
                lc.RSP.S_VR,
            )
            if isinstance(result, (bytearray,)) and len(result) > 0:
                info_data.plc = lm.ba_to_ustr(result)

            result = self._send_recive(
                lc.CMD.R_VR,
                struct.pack("!B", lc.ParRVR.OPTIONS),
                lc.RSP.S_VR,
            )
            if isinstance(result, (bytearray,)) and len(result) > 0:
                info_data.option_bits = lm.ba_to_ustr(result)

            result = self._send_recive(
                lc.CMD.R_VR,
                struct.pack("!B", lc.ParRVR.ID),
                lc.RSP.S_VR,
            )
            if isinstance(result, (bytearray,)) and len(result) > 0:
                info_data.id_number = lm.ba_to_ustr(result)

            if "itnc" in info_data.control.lower():
                info_data.release = "not supported"
            else:
                result = self._send_recive(
                    lc.CMD.R_VR,
                    struct.pack("!B", lc.ParRVR.RELEASE_TYPE),
                    lc.RSP.S_VR,
                )
                if isinstance(result, (bytearray,)) and len(result) > 0:
                    info_data.release = lm.ba_to_ustr(result)

            result = self._send_recive(
                lc.CMD.R_VR,
                struct.pack("!B", lc.ParRVR.SPLC_VERSION),
                lc.RSP.S_VR,
            )
            if isinstance(result, (bytearray,)) and len(result) > 0:
                info_data.splc = lm.ba_to_ustr(result)
            else:
                info_data.splc = "not supported"

            self._logger.debug("got version info: %s", info_data)
            self._versions = info_data

        return self._versions

    def program_status(self) -> lc.PgmState:
        """
        Ret status code of currently active program.
        Requires access level ``DNC`` to work.
        See https://github.com/tfischer73/Eclipse-Plugin-Heidenhain/issues/1
        """
        if not self.login(login=lc.Login.DNC):
            self._logger.warning("could not log in as user DNC")
            return lc.PgmState.UNDEFINED

        payload = struct.pack("!H", lc.ParRRI.PGM_STATE)
        result = self._send_recive(lc.CMD.R_RI, payload, lc.RSP.S_RI)
        if isinstance(result, (bytearray,)):
            self._logger.debug(
                "successfully read state of active program: %s",
                struct.unpack("!H", result)[0],
            )
            return lc.PgmState(struct.unpack("!H", result)[0])
        self._logger.warning("an error occurred while querying program state")
        return lc.PgmState.UNDEFINED

    def program_stack(self) -> Union[ld.StackState, None]:
        """
        Get path of currently active nc program(s) and current line number.
        Requires access level ``DNC`` to work.
        See https://github.com/tfischer73/Eclipse-Plugin-Heidenhain/issues/1
        """
        if not self.login(login=lc.Login.DNC):
            self._logger.warning("could not log in as user DNC")
            return None

        payload = struct.pack("!H", lc.ParRRI.SELECTED_PGM)
        result = self._send_recive(lc.CMD.R_RI, payload, lc.RSP.S_RI)
        if isinstance(result, (bytearray,)) and len(result) > 0:
            stack_info = lm.decode_stack_info(result)
            self._logger.debug("successfully read active program stack: %s", stack_info)
            return stack_info
        self._logger.warning("an error occurred while querying active program state")

        return None

    def execution_state(self) -> lc.ExecState:
        """
        Get status code of program state
        Requires access level ``DNC`` to work.
        See https://github.com/drunsinn/pyLSV2/issues/1
        """
        if not self.login(login=lc.Login.DNC):
            self._logger.warning("could not log in as user DNC")
            return lc.ExecState.UNDEFINED

        payload = struct.pack("!H", lc.ParRRI.EXEC_STATE)

        result = self._send_recive(lc.CMD.R_RI, payload, lc.RSP.S_RI)
        if isinstance(result, (bytearray,)):
            self._logger.debug("read execution state %d", struct.unpack("!H", result)[0])
            return lc.ExecState(struct.unpack("!H", result)[0])
        self._logger.warning("an error occurred while querying execution state")
        return lc.ExecState.UNDEFINED

    def directory_info(self, remote_directory: str = "") -> ld.DirectoryEntry:
        """
        Read information about the current working directory on the control.
        Requires access level ``FILETRANSFER`` to work.

        :param remote_directory: optional. change working directory before reading info
        """
        if not self.login(lc.Login.FILETRANSFER):
            self._logger.warning("could not log in as user FILE")
            return ld.DirectoryEntry()

        if len(remote_directory) > 0 and self.change_directory(remote_directory) is False:
            self._logger.warning(
                "could not change current directory to read directory info for %s",
                remote_directory,
            )
            return ld.DirectoryEntry()
        result = self._send_recive(lc.CMD.R_DI, None, lc.RSP.S_DI)
        if isinstance(result, (bytearray,)) and len(result) > 0:
            dir_info = lm.decode_directory_info(result)
            self._logger.debug("successfully received directory information for %s", dir_info.path)
            return dir_info
        self._logger.warning("an error occurred while querying directory info")

        return ld.DirectoryEntry()

    def change_directory(self, remote_directory: str) -> bool:
        """
        change the current working directory on the control.
        Requires access level ``FILETRANSFER`` to work.
        Returns ``True`` if completed successfully.

        :param remote_directory: path of directory on the control
        """
        if not self.login(lc.Login.FILETRANSFER):
            self._logger.warning("could not log in as user FILE")
            return False

        dir_path = remote_directory.replace("/", lc.PATH_SEP)

        payload = lm.ustr_to_ba(dir_path)

        result = self._send_recive(lc.CMD.C_DC, payload, lc.RSP.T_OK)
        if isinstance(result, (bool,)) and result is True:
            self._logger.debug("changed working directory to %s", dir_path)
            return True

        if remote_directory == self.directory_info().path:
            self._logger.info("control responded as if the dir change did not work but path is still correct...")
            return True

        self._logger.warning("an error occurred while changing directory to %s", dir_path)
        return False

    def file_info(self, remote_file_path: str) -> Union[ld.FileEntry, None]:
        """
        Query information about a file.
        Requires access level ``FILETRANSFER`` to work.
        Returns ``None`` of file doesn't exist or missing access rights

        :param remote_file_path: path of file on the control

        :raises LSV2ProtocolException: if an error occurred during reading of file info
        """
        if not self.login(lc.Login.FILETRANSFER):
            self._logger.warning("could not log in as user FILE")
            return None

        file_path = remote_file_path.replace("/", lc.PATH_SEP)
        payload = lm.ustr_to_ba(file_path)

        result = self._send_recive(lc.CMD.R_FI, payload, lc.RSP.S_FI)
        if isinstance(result, (bytearray,)) and len(result) > 0:
            file_info = lm.decode_file_system_info(result, self._versions.type)
            self._logger.debug("received file information for %s", file_info.name)
            return file_info

        if self.last_error.e_code == lc.LSV2StatusCode.T_ER_NO_FILE:
            self._logger.debug("file does not exist")
            return None

        self._logger.error(
            "an error occurred while querying file info for %s : '%s'",
            remote_file_path,
            lt.get_error_text(self.last_error),
        )
        return None

    def directory_content(self) -> List[ld.FileEntry]:
        """
        Query content of current working directory from the control. In some situations it is necessary to
        fist call :py:func:`~pyLSV2.LSV2.directory_info` or else the attributes won't be correct.
        Requires access level ``FILETRANSFER`` to work.
        """

        if not self.login(lc.Login.FILETRANSFER):
            self._logger.warning("could not log in as user FILE")
            return []

        dir_content: List[ld.FileEntry] = []
        payload = bytearray(struct.pack("!B", lc.ParRDR.SINGLE))

        result = self._send_recive_block(lc.CMD.R_DR, payload, lc.RSP.S_DR)
        if isinstance(result, (list,)):
            for entry in result:
                dir_content.append(lm.decode_file_system_info(entry, self._versions.type))

            self._logger.debug("received %d packages for directory content", len(dir_content))
        else:
            self._logger.warning(
                "an error occurred while directory content info: '%s'",
                lt.get_error_text(self.last_error),
            )
        return dir_content

    def drive_info(self) -> List[ld.DriveEntry]:
        """
        Read info all drives and partitions from the control.
        Requires access level ``FILETRANSFER`` to work.

        Might not work on older controls or on old windows programming stations?
        """

        if not self.login(lc.Login.FILETRANSFER):
            self._logger.warning("could not log in as user FILE")
            return []

        drives_list: List[ld.DriveEntry] = []
        payload = bytearray(struct.pack("!B", lc.ParRDR.DRIVES))
        result = self._send_recive_block(lc.CMD.R_DR, payload, lc.RSP.S_DR)
        if isinstance(result, (list,)):
            for entry in result:
                drives_list.extend(lm.decode_drive_info(entry))

            self._logger.debug(
                "successfully received %d packages for drive information %s",
                len(result),
                drives_list,
            )
        else:
            self._logger.warning(
                "an error occurred while reading drive info: '%s'",
                lt.get_error_text(self.last_error),
            )

        if "TNC:" not in [d.name for d in drives_list]:
            self._logger.warning(
                "an error occurred while parsing drive info. this might be either a problem with the decoding or the control does not support this function!"
            )
            return []
        return drives_list

    def make_directory(self, dir_path: str) -> bool:
        """
        Create a directory on control. If necessary also creates parent directories.
        Requires access level ``FILETRANSFER`` to work.
        Returns ``True`` if completed successfully.

        :param dir_path: path of directory on the control
        """
        if not self.login(lc.Login.FILETRANSFER):
            self._logger.warning("could not log in as user FILE")
            return False

        path_parts = dir_path.replace("/", lc.PATH_SEP).split(lc.PATH_SEP)  # convert path
        path_to_check = ""

        for part in path_parts:
            path_to_check += part + lc.PATH_SEP
            # no file info -> does not exist and has to be created
            if self.file_info(path_to_check) is None:
                payload = lm.ustr_to_ba(path_to_check)

                result = self._send_recive(lc.CMD.C_DM, payload, lc.RSP.T_OK)
                if isinstance(result, (bool,)) and result is True:
                    self._logger.debug("Directory created successfully")
                else:
                    self._logger.warning(
                        "an error occurred while creating directory %s: '%s'",
                        dir_path,
                        lt.get_error_text(self.last_error),
                    )
                    return False
            else:
                self._logger.debug("nothing to do as this segment already exists")
        return True

    def delete_empty_directory(self, dir_path: str) -> bool:
        """
        Delete empty directory on control.
        Requires access level ``FILETRANSFER`` to work.
        Returns ``True`` if completed successfully.

        :param file_path: path of directory on the control
        """
        if not self.login(lc.Login.FILETRANSFER):
            self._logger.warning("could not log in as user FILE")
            return False

        dir_path = dir_path.replace("/", lc.PATH_SEP)
        payload = lm.ustr_to_ba(dir_path)

        result = self._send_recive(lc.CMD.C_DD, payload, lc.RSP.T_OK)
        if isinstance(result, (bool)) and result is True:
            self._logger.debug("successfully deleted directory %s", dir_path)
            return True

        if self.last_error.e_code == lc.LSV2StatusCode.T_ER_NO_DIR:
            self._logger.debug("noting to do, directory %s didn't exist", dir_path)
            return True

        if self.last_error.e_code == lc.LSV2StatusCode.T_ER_DEL_DIR:
            self._logger.debug("could not delete directory %s since it is not empty", dir_path)
            return False

        self._logger.warning(
            "an error occurred while deleting directory %s",
            dir_path,
        )
        return False

    def delete_file(self, file_path: str) -> bool:
        """
        Delete file on control.
        Requires access level ``FILETRANSFER`` to work.
        Returns ``True`` if completed successfully.

        :param file_path: path of file on the control
        """
        if not self.login(lc.Login.FILETRANSFER):
            self._logger.warning("could not log in as user FILE")
            return False

        file_path = file_path.replace("/", lc.PATH_SEP)
        payload = lm.ustr_to_ba(file_path)

        if self._send_recive(lc.CMD.C_FD, payload, lc.RSP.T_OK):
            self._logger.debug("successfully deleted file %s", file_path)
            return True

        if self.last_error.e_code == lc.LSV2StatusCode.T_ER_NO_FILE:
            self._logger.debug("noting to do, file %s didn't exist", file_path)
            return True

        if self.last_error.e_code == lc.LSV2StatusCode.T_ER_NO_DELETE:
            self._logger.info("could not delete file %s since it is in use", file_path)
            return False

        self._logger.warning(
            "an error occurred while deleting file %s",
            file_path,
        )
        return False

    def copy_remote_file(self, source_path: str, target_path: str) -> bool:
        """
        Copy file on control from one place to another.
        Requires access level ``FILETRANSFER`` to work.
        Returns ``True`` if completed successfully.

        :param source_path: path of file on the control
        :param target_path: path of target location

        :raises LSV2StateException: if the selected path could not be found or
                                    the path is not accessible
        """
        if not self.login(lc.Login.FILETRANSFER):
            self._logger.warning("could not log in as user FILE")
            return False

        source_path = source_path.replace("/", lc.PATH_SEP)
        target_path = target_path.replace("/", lc.PATH_SEP)

        if lc.PATH_SEP in source_path:
            # change directory
            source_file_name = source_path.split(lc.PATH_SEP)[-1]
            source_directory = source_path.rstrip(source_file_name)
            if not self.change_directory(remote_directory=source_directory):
                raise LSV2StateException("could not open the source directory")
        else:
            source_file_name = source_path
            source_directory = "."

        if target_path.endswith(lc.PATH_SEP):
            target_path += source_file_name

        payload = lm.ustr_to_ba(source_file_name)
        payload.extend(lm.ustr_to_ba(target_path))
        self._logger.debug(
            "prepare to copy file %s from %s to %s",
            source_file_name,
            source_directory,
            target_path,
        )
        if self._send_recive(lc.CMD.C_FC, payload, lc.RSP.T_OK):
            self._logger.debug("successfully copied file %s", source_path)
            return True

        self._logger.warning("an error occurred copying file %s to %s", source_path, target_path)
        return False

    def move_file(self, source_path: str, target_path: str) -> bool:
        """
        Move file on control from one place to another.
        Requires access level ``FILETRANSFER`` to work.
        Returns ``True`` if creating directory was successful.

        :param source_path: path of file on the control
        :param target_path: path of target location with or without filename

        :raises LSV2StateException: if the selected path could not be found or
                                    the path is not accessible
        """
        source_path = source_path.replace("/", lc.PATH_SEP)
        target_path = target_path.replace("/", lc.PATH_SEP)

        if not self.login(lc.Login.FILETRANSFER):
            self._logger.warning("could not log in as user FILE")
            return False

        if lc.PATH_SEP in source_path:
            source_file_name = source_path.split(lc.PATH_SEP)[-1]
            source_directory = source_path.rstrip(source_file_name)
            if not self.change_directory(remote_directory=source_directory):
                raise LSV2StateException("could not open the source directory")
        else:
            source_file_name = source_path
            source_directory = "."

        if target_path.endswith(lc.PATH_SEP):
            target_path += source_file_name

        payload = lm.ustr_to_ba(source_file_name)
        payload.extend(lm.ustr_to_ba(target_path))

        self._logger.debug(
            "prepare to move file %s from %s to %s",
            source_file_name,
            source_directory,
            target_path,
        )
        if self._send_recive(lc.CMD.C_FR, payload, lc.RSP.T_OK):
            self._logger.debug("successfully moved file %s", source_path)
            return True

        if self.last_error.e_code == lc.LSV2StatusCode.T_ER_FILE_EXISTS:
            self._logger.info(
                "could not move file %s to %s since already exists",
                source_path,
                target_path,
            )
            return False

        if self.last_error.e_code == lc.LSV2StatusCode.T_ER_NO_FILE:
            self._logger.info(
                "could not move file since either source or target path does not exist",
            )
            return False

        self._logger.warning("an error occurred moving file %s to %s", source_path, target_path)
        return False

    def send_file(
        self,
        local_path: Union[str, pathlib.Path],
        remote_path: str,
        override_file: bool = False,
        binary_mode: bool = False,
    ) -> bool:
        """
        Upload a file to control
        Requires access level ``FILETRANSFER`` to work.
        Returns ``True`` if completed successfully.

        :param local_path: path of file to be sent to the control
        :param remote_path: path with or without the file name on the control
        :param override_file: flag if file should be replaced if it already exists
        :param binary_mode: flag if binary transfer mode should be used, if not set the
                            file name is checked for known binary file type

        :raises LSV2StateException: if local file could not be opened,
                                    destination directory could not be accessed or
                                    destination file could not be deleted
        """
        if not self.login(lc.Login.FILETRANSFER):
            self._logger.warning("could not log in as user FILE")
            return False

        if isinstance(local_path, (str,)):
            local_file = pathlib.Path(local_path)
        else:
            local_file = local_path

        if not local_file.is_file():
            self._logger.warning("the supplied path %s did not resolve to a file", local_file)
            raise LSV2StateException("local file does not exist! {}".format(local_file))

        remote_path = remote_path.replace("/", lc.PATH_SEP)

        if lc.PATH_SEP in remote_path:
            if remote_path.endswith(lc.PATH_SEP):  # no filename given
                remote_file_name = local_file.name
                remote_directory = remote_path
            else:
                remote_file_name = remote_path.split(lc.PATH_SEP)[-1]
                remote_directory = remote_path.rstrip(remote_file_name)
                if not self.change_directory(remote_directory=remote_directory):
                    raise LSV2StateException("could not open the destination directory {}".format(remote_directory))
        else:
            remote_file_name = remote_path
            remote_directory = self.directory_info().path  # get pwd
        remote_directory = remote_directory.rstrip(lc.PATH_SEP)

        if not self.directory_info(remote_directory):
            self._logger.debug("remote path does not exist, create directory(s)")
            self.make_directory(remote_directory)

        remote_info = self.file_info(remote_directory + lc.PATH_SEP + remote_file_name)

        if remote_info:
            self._logger.debug("remote path exists and points to file's")
            if override_file:
                if not self.delete_file(remote_directory + lc.PATH_SEP + remote_file_name):
                    raise LSV2StateException(
                        "something went wrong while deleting file {}".format(remote_directory + lc.PATH_SEP + remote_file_name)
                    )
            else:
                self._logger.warning("remote file already exists, override was not set")
                return False

        self._logger.debug(
            "ready to send file from %s to %s",
            local_file,
            remote_directory + lc.PATH_SEP + remote_file_name,
        )

        payload = lm.ustr_to_ba(remote_directory + lc.PATH_SEP + remote_file_name)
        if binary_mode or lm.is_file_binary(local_path):
            payload.append(lc.MODE_BINARY)
            self._logger.debug("selecting binary transfer mode")
        else:
            payload.append(lc.MODE_NON_BIN)
            self._logger.debug("selecting non binary transfer mode")

        self._llcom.telegram(
            lc.CMD.C_FL,
            payload,
        )

        if self._llcom.last_response in lc.RSP.T_OK:
            with local_file.open("rb") as input_buffer:
                while True:
                    # use current buffer size but reduce by 10 to make sure it fits together with command and size
                    buffer = bytearray(input_buffer.read(self._llcom.buffer_size - 8 - 2))
                    if not buffer:
                        # finished reading file
                        break

                    result = self._llcom.telegram(
                        lc.RSP.S_FL,
                        buffer,
                    )
                    if self._llcom.last_response in lc.RSP.T_OK:
                        pass
                    else:
                        if self._llcom.last_response in [lc.RSP.T_ER, lc.RSP.T_BD]:
                            self._logger.info(
                                "control returned error '%s' which translates to '%s'",
                                self.last_error,
                                lt.get_error_text(self.last_error),
                            )
                        else:
                            # if len(result) == 2:

                            self._logger.info(
                                "could not send data, received unexpected response '%s' with data 0x%s",
                                self._llcom.last_response,
                                result.hex(),
                            )
                        return False

            # signal that no more data is being sent
            if self._secure_file_send:
                if not self._send_recive(lc.RSP.T_FD, None, lc.RSP.T_OK):
                    self._logger.warning(
                        "could not send end of transmission telegram, got response '%s'",
                        self._llcom.last_response,
                    )
                    return False
            else:
                if not self._send_recive(lc.RSP.T_FD, None, lc.RSP.NONE):
                    self._logger.warning(
                        "could not send end of transmission telegram, got response '%s'",
                        self._llcom.last_response,
                    )
                    return False

        else:
            if self._llcom.last_response is lc.RSP.T_ER:
                self._logger.warning(
                    "error received, %s '%s'",
                    self.last_error,
                    lt.get_error_text(self.last_error),
                )
            else:
                self._logger.warning("could not send file with error %s", self._llcom.last_response)
            return False

        return True

    def recive_file(
        self,
        remote_path: str,
        local_path: Union[str, pathlib.Path],
        override_file: bool = False,
        binary_mode: bool = False,
    ) -> bool:
        """
        Download a file from control.
        Requires access level ``FILETRANSFER`` to work.
        Returns ``True`` if completed successfully.

        :param remote_path: path of file on the control
        :param local_path: local path of destination with or without file name
        :param override_file: flag if file should be replaced if it already exists
        :param binary_mode: flag if binary transfer mode should be used, if not set the
                            file name is checked for known binary file type
        """
        if not self.login(lc.Login.FILETRANSFER):
            self._logger.warning("could not log in as user FILE")
            return False

        if isinstance(local_path, (str,)):
            local_file = pathlib.Path(local_path)
        else:
            local_file = local_path

        remote_path = remote_path.replace("/", lc.PATH_SEP)
        remote_file_info = self.file_info(remote_path)
        if not remote_file_info:
            self._logger.warning("remote file does not exist: %s", remote_path)
            return False

        if local_file.is_dir():
            local_file.joinpath(remote_path.split("/")[-1])
        elif local_file.is_file():
            # self._logger.debug("local path exists and points to file")
            if not override_file:
                self._logger.warning("local file already exists and override was not set. nothing to do")
                return False
            local_file.unlink()

        self._logger.debug("loading file from %s to %s", remote_path, local_file)

        payload = lm.ustr_to_ba(remote_path)

        if binary_mode or lm.is_file_binary(remote_path):
            payload.append(lc.MODE_BINARY)  # force binary transfer
            self._logger.debug("using binary transfer mode")
        else:
            payload.append(lc.MODE_NON_BIN)
            self._logger.debug("using non binary transfer mode")

        content = self._llcom.telegram(
            lc.CMD.R_FL,
            payload,
        )

        with local_file.open("wb") as out_file:
            if self._llcom.last_response in lc.RSP.S_FL:
                if binary_mode:
                    out_file.write(content)
                else:
                    out_file.write(content.replace(b"\x00", b"\r\n"))
                self._logger.debug("received first block of file file %s", remote_path)

                while True:
                    content = self._llcom.telegram(
                        lc.RSP.T_OK,
                    )
                    if self._llcom.last_response in lc.RSP.S_FL:
                        if binary_mode:
                            out_file.write(content)
                        else:
                            out_file.write(content.replace(b"\x00", b"\r\n"))
                        self._logger.debug("received %d more bytes for file", len(content))
                    elif self._llcom.last_response in lc.RSP.T_FD:
                        self._logger.info("finished loading file")
                        break
                    else:
                        self._logger.warning(
                            "something went wrong while receiving file data %s",
                            remote_path,
                        )
                        if self._llcom.last_response is lc.RSP.T_ER or self._llcom.last_response is lc.RSP.T_BD:
                            self._logger.warning(
                                "an error occurred while loading the first block of data %s '%s'",
                                self.last_error,
                                lt.get_error_text(self.last_error),
                            )
                        return False
            else:
                if self._llcom.last_response is lc.RSP.T_ER or self._llcom.last_response is lc.RSP.T_BD:
                    self._logger.warning(
                        "an error occurred while loading the first block of data for file %s, %s '%s'",
                        remote_path,
                        self.last_error,
                        lt.get_error_text(self.last_error),
                    )
                else:
                    self._logger.warning("could not load file with error %s", self._llcom.last_response)
                return False

        self._logger.info(
            "received %d bytes transfer complete for file %s to %s",
            local_file.stat().st_size,
            remote_path,
            local_file,
        )

        return True

    def read_plc_memory(
        self, first_element: int, mem_type: lc.MemoryType, number_of_elements: int = 1
    ) -> List[Union[None, int, float, str]]:
        """
        Read data from plc memory.
        Requires access level ``PLCDEBUG`` to work.

        :param first_element: which memory location should be read, starts at 0 up to the max number for each type
        :param mem_type: what datatype to read
        :param number_of_elements: how many elements should be read

        :raises LSV2InputException: if unknowns memory type is requested or if the to many elements are requested
        :raises LSV2DataException: if number of received values does not match the number of expected
        """

        if self._sys_par.lsv2_version != -1:
            self._read_parameters()

        if not self.login(login=lc.Login.PLCDEBUG):
            self._logger.warning("could not log in as user PLCDEBUG")
            return []

        if mem_type is lc.MemoryType.MARKER:
            start_address = self._sys_par.markers_start_address
            max_elements = self._sys_par.number_of_markers
            mem_byte_count = 1
            unpack_string = "!?"
        elif mem_type is lc.MemoryType.INPUT:
            start_address = self._sys_par.inputs_start_address
            max_elements = self._sys_par.number_of_inputs
            mem_byte_count = 1
            unpack_string = "!?"
        elif mem_type is lc.MemoryType.OUTPUT:
            start_address = self._sys_par.outputs_start_address
            max_elements = self._sys_par.number_of_outputs
            mem_byte_count = 1
            unpack_string = "!?"
        elif mem_type is lc.MemoryType.COUNTER:
            start_address = self._sys_par.counters_start_address
            max_elements = self._sys_par.number_of_counters
            mem_byte_count = 1
            unpack_string = "!?"
        elif mem_type is lc.MemoryType.TIMER:
            start_address = self._sys_par.timers_start_address
            max_elements = self._sys_par.number_of_timers
            mem_byte_count = 1
            unpack_string = "!?"
        elif mem_type is lc.MemoryType.BYTE:
            start_address = self._sys_par.words_start_address
            max_elements = self._sys_par.number_of_words * 2
            mem_byte_count = 1
            unpack_string = "<b"
        elif mem_type is lc.MemoryType.WORD:
            start_address = self._sys_par.words_start_address
            max_elements = self._sys_par.number_of_words
            mem_byte_count = 2
            unpack_string = "<h"
        elif mem_type is lc.MemoryType.DWORD:
            start_address = self._sys_par.words_start_address
            max_elements = self._sys_par.number_of_words / 4
            mem_byte_count = 4
            unpack_string = "<l"
        elif mem_type is lc.MemoryType.STRING:
            start_address = self._sys_par.strings_start_address
            max_elements = self._sys_par.number_of_strings
            mem_byte_count = self._sys_par.max_string_lenght
            unpack_string = "{}s".format(mem_byte_count)
        elif mem_type is lc.MemoryType.INPUT_WORD:
            start_address = self._sys_par.input_words_start_address
            max_elements = self._sys_par.number_of_input_words
            mem_byte_count = 2
            unpack_string = "<H"
        elif mem_type is lc.MemoryType.OUTPUT_WORD:
            start_address = self._sys_par.output_words_start_address
            max_elements = self._sys_par.number_of_output_words
            mem_byte_count = 2
            unpack_string = "<H"
        elif mem_type is lc.MemoryType.OUTPUT_DWORD:
            start_address = self._sys_par.output_words_start_address
            max_elements = self._sys_par.number_of_output_words / 4
            mem_byte_count = 4
            unpack_string = "<l"
        elif mem_type is lc.MemoryType.INPUT_DWORD:
            start_address = self._sys_par.input_words_start_address
            max_elements = self._sys_par.number_of_input_words / 4
            mem_byte_count = 4
            unpack_string = "<l"
        else:
            raise LSV2InputException("unknown address type")

        if (first_element + number_of_elements) > max_elements:
            raise LSV2InputException(
                "highest address is %d but address of last requested element is %d" % (max_elements, (first_element + number_of_elements))
            )

        plc_values: List[Union[None, int, float, str]] = []

        if mem_type is lc.MemoryType.STRING:
            for i in range(number_of_elements):
                address = start_address + first_element * mem_byte_count + i * mem_byte_count

                payload = bytearray()
                payload.extend(struct.pack("!L", address))
                payload.extend(struct.pack("!B", mem_byte_count))
                result = self._send_recive(lc.CMD.R_MB, payload, lc.RSP.S_MB)
                if isinstance(result, (bytearray,)):
                    logging.debug(
                        "read string %d with length %d",
                        (first_element + i),
                        len(result),
                    )

                    unpack_string = "{}s".format(len(result))

                    plc_values.append(lm.ba_to_ustr(struct.unpack(unpack_string, result)[0]))
                else:
                    logging.error(
                        "failed to read string %d from address %d",
                        (first_element + i),
                        address,
                    )
                    return []
        else:
            max_elements_per_transfer = math.floor(255 / mem_byte_count) - 1  # subtract 1 for safety
            num_groups = math.ceil(number_of_elements / max_elements_per_transfer)
            logging.debug(
                "memory type allows %d elements per telegram, split request into %d group(s)",
                max_elements_per_transfer,
                num_groups,
            )

            remaining_elements = number_of_elements
            first_element_in_group = first_element

            for i in range(num_groups):
                # determine number of elements for this group
                if remaining_elements > max_elements_per_transfer:
                    elements_in_group = max_elements_per_transfer
                else:
                    elements_in_group = remaining_elements

                address = start_address + first_element_in_group * mem_byte_count

                logging.debug("current transfer group %d has %d elements", i, elements_in_group)

                payload = bytearray()
                payload.extend(struct.pack("!L", address))
                payload.extend(struct.pack("!B", elements_in_group * mem_byte_count))
                result = self._send_recive(lc.CMD.R_MB, payload, lc.RSP.S_MB)
                if isinstance(result, (bytearray,)):
                    logging.debug(
                        "read %d value(s) from address %d",
                        elements_in_group,
                        first_element_in_group,
                    )
                    for j in range(0, len(result), mem_byte_count):
                        plc_values.append(struct.unpack(unpack_string, result[j : j + mem_byte_count])[0])
                else:
                    logging.error(
                        "failed to read value from address %d",
                        start_address + first_element_in_group,
                    )
                    return []

                remaining_elements -= elements_in_group
                first_element_in_group += first_element_in_group + elements_in_group

            logging.debug("read a total of %d value(s)", len(plc_values))
        if len(plc_values) != number_of_elements:
            raise LSV2DataException(
                "number of received values %d is not equal to number of requested %d" % (len(plc_values), number_of_elements)
            )
        return plc_values

    def read_plc_address(self, address: str) -> Union[None, int, float, str]:
        """
        read from plc memory using the nativ addressing scheme of the control
        Requires access level ``PLCDEBUG`` to work.

        :param address: address of the plc memory location in the format used by the nc like W1090, M0 or S20

        :raises LSV2InputException: if unknowns memory type is requested or if the to many elements are requested
        :raises LSV2DataException: if number of received values does not match the number of expected
        """

        m_type, m_num = lm.decode_plc_memory_address(address)

        if m_type is None or m_num is None:
            raise LSV2InputException("could not translate address %s to valid memory location" % address)

        return self.read_plc_memory(m_num, m_type, 1)[0]

    def set_keyboard_access(self, unlocked: bool) -> bool:
        """
        Enable or disable the keyboard on the control.
        Requires access level ``MONITOR`` to work.
        Returns ``True`` if completed successfully.

        :param unlocked: if ``True`` unlocks the keyboard so it can be used. If ``False``, input is set to locked
        """
        if self.versions.is_tnc7():
            self._logger.warning("this function might not be supported on TNC7")

        if not self.login(lc.Login.MONITOR):
            self._logger.warning("clould not log in as user MONITOR")
            return False

        payload = bytearray()
        if unlocked:
            payload.extend(struct.pack("!B", 0x00))
        else:
            payload.extend(struct.pack("!B", 0x01))

        result = self._send_recive(lc.CMD.C_LK, payload, lc.RSP.T_OK)
        if result:
            if unlocked:
                self._logger.debug("command to unlock keyboard was successful")
            else:
                self._logger.debug("command to lock keyboard was successful")
            return True
        self._logger.warning("an error occurred changing the state of the keyboard lock")
        return False

    def get_machine_parameter(self, name: str) -> str:
        """
        Read machine parameter from control.
        Requires access level ``INSPECT`` level to work.

        :param name: name of the machine parameter.
        """
        if not self.login(lc.Login.INSPECT):
            self._logger.warning("clould not log in as user INSPECT")
            return ""

        if isinstance(name, (int,)):
            name = str(name)

        payload = lm.ustr_to_ba(name)

        result = self._send_recive(lc.CMD.R_MC, payload, lc.RSP.S_MC)
        if isinstance(result, (bytearray,)) and len(result) > 0:
            value = lm.ba_to_ustr(result)
            self._logger.debug("machine parameter %s has value %s", name, value)
            return value

        self._logger.warning("an error occurred while reading machine parameter %s", name)
        return ""

    def set_machine_parameter(self, name: str, value: str, safe_to_disk: bool = False) -> bool:
        """
        Set machine parameter on control. Writing a parameter takes some time, make sure to set timeout
        sufficiently high!
        Requires access ``PLCDEBUG`` level to work.
        Returns ``True`` if completed successfully.

        :param name: name of the machine parameter. For iTNC the parameter number hase to be converted to string
        :param value: new value of the machine parameter. There is no type checking, if the value can not be
                        converted by the control an error will be sent.
        :param safe_to_disk: If True the new value will be written to the harddisk and stay permanent.
                        If False (default) the value will only be available until the next reboot.
        """
        if not self.login(lc.Login.PLCDEBUG):
            self._logger.warning("clould not log in as user PLCDEBUG")
            return False

        payload = bytearray()
        if safe_to_disk:
            payload.extend(struct.pack("!L", 0x00))
        else:
            payload.extend(struct.pack("!L", 0x01))
        payload.extend(lm.ustr_to_ba(name))
        payload.extend(lm.ustr_to_ba(value))

        result = self._send_recive(lc.CMD.C_MC, payload, lc.RSP.T_OK)
        if result:
            self._logger.debug(
                "setting of machine parameter %s to value %s was successful",
                name,
                value,
            )
            return True

        self._logger.warning(
            "an error occurred while setting machine parameter %s to value %s",
            name,
            value,
        )
        return False

    def send_key_code(self, key_code: Union[lc.KeyCode, lc.OldKeyCode]) -> bool:
        """
        Send key code to control. Behaves as if the associated key was pressed on the keyboard.
        Requires access ``MONITOR`` level to work.
        To work correctly you first have to lock the keyboard and unlock it afterwards!:

        .. code-block:: python

            set_keyboard_access(False)
            send_key_code(KeyCode.CE)
            set_keyboard_access(True)

        Returns ``True`` if completed successfully.

        :param key_code: code number of the keyboard key
        """
        if self.versions.is_tnc7():
            self._logger.warning("this function might not be supported on TNC7")

        if not self.login(lc.Login.MONITOR):
            self._logger.warning("clould not log in as user MONITOR")
            return False

        payload = bytearray()
        payload.extend(struct.pack("!H", key_code))

        result = self._send_recive(lc.CMD.C_EK, payload, lc.RSP.T_OK)
        if result:
            self._logger.debug("sending the key code %d was successful", key_code)
            return True

        self._logger.warning("an error occurred while sending the key code %d", key_code)
        return False

    def spindle_tool_status(self) -> Union[ld.ToolInformation, None]:
        """
        Get information about the tool currently in the spindle
        Requires access level ``DNC`` to work.
        """
        if not self.login(lc.Login.DNC):
            self._logger.warning("clould not log in as user DNC")
            return None

        payload = bytearray()
        payload.extend(struct.pack("!H", lc.ParRRI.CURRENT_TOOL))

        result = self._send_recive(lc.CMD.R_RI, payload, lc.RSP.S_RI)
        if isinstance(result, (bytearray,)) and len(result) > 0:
            tool_info = lm.decode_tool_info(result)
            self._logger.debug("successfully read info on current tool: %s", tool_info)
            return tool_info
        self._logger.warning("an error occurred while querying current tool information. This does not work for all control types")
        return None

    def override_state(self) -> Union[ld.OverrideState, None]:
        """
        Get information about the override info.
        Requires access level ``DNC`` to work.
        """
        if not self.login(lc.Login.DNC):
            self._logger.warning("clould not log in as user DNC")
            return None

        payload = bytearray()
        payload.extend(struct.pack("!H", lc.ParRRI.OVERRIDE))

        result = self._send_recive(lc.CMD.R_RI, payload, lc.RSP.S_RI)
        if isinstance(result, (bytearray,)) and len(result) > 0:
            override_info = lm.decode_override_state(result)
            self._logger.debug("successfully read override info: %s", override_info)
            return override_info
        self._logger.warning("an error occurred while querying current override information. This does not work for all control types")
        return None

    def get_error_messages(self) -> List[ld.NCErrorMessage]:
        """
        Get information about the first or next error displayed on the control
        Requires access level ``DNC`` to work.
        Returns error list of error messages
        """
        messages: List[ld.NCErrorMessage] = []
        if not self.login(lc.Login.DNC):
            self._logger.warning("clould not log in as user DNC")
            return []

        payload = bytearray()
        payload.extend(struct.pack("!H", lc.ParRRI.FIRST_ERROR))

        result = self._send_recive(lc.CMD.R_RI, payload, lc.RSP.S_RI)
        if isinstance(result, (bytearray,)) and len(result) > 0:
            messages.append(lm.decode_error_message(result))
            payload = bytearray()
            payload.extend(struct.pack("!H", lc.ParRRI.NEXT_ERROR))
            result = self._send_recive(lc.CMD.R_RI, payload, lc.RSP.S_RI)
            self._logger.debug("successfully read first error but further errors")

            while isinstance(result, (bytearray,)):
                messages.append(lm.decode_error_message(result))
                result = self._send_recive(lc.CMD.R_RI, payload, lc.RSP.S_RI)

            if self.last_error.e_code is lc.LSV2StatusCode.T_ER_NO_NEXT_ERROR:
                self._logger.debug("successfully read all errors")
            else:
                self._logger.warning("an error occurred while querying error information.")

            return messages

        if self.last_error.e_code is lc.LSV2StatusCode.T_ER_NO_NEXT_ERROR:
            self._logger.debug("successfully read first error but no error active")
            return messages

        self._logger.warning("an error occurred while querying error information. This does not work for all control types")

        return []

    def _walk_dir(self, descend: bool = True) -> List[str]:
        """
        helper function to recursively search in directories for files.
        Requires access level ``FILETRANSFER`` to work.

        :param descend: control if search should run recursively
        """
        if not self.login(lc.Login.FILETRANSFER):
            self._logger.warning("clould not log in as user FILE")
            return []

        current_path = self.directory_info().path.replace("/", lc.PATH_SEP)
        content: List[str] = []

        for entry in self.directory_content():
            if entry.name == "." or entry.name == ".." or entry.name.endswith(":"):
                continue
            current_fs_element = str(current_path + entry.name).replace("/", lc.PATH_SEP)
            if entry.is_directory is True and descend is True:
                if self.change_directory(current_fs_element):
                    content.extend(self._walk_dir())
            else:
                content.append(current_fs_element)
        self.change_directory(current_path)
        return content

    def get_file_list(self, path: str = "", descend: bool = True, pattern: str = "") -> List[str]:
        """
        Get list of files in directory structure.
        Requires access level ``FILETRANSFER`` to work.

        :param path: path of the directory where files should be searched. if None than the current directory is used
        :param descend: control if search should run recursively
        :param pattern: regex string to filter the file names
        """
        if not self.login(lc.Login.FILETRANSFER):
            self._logger.warning("clould not log in as user FILE")
            return []

        if self.change_directory(path) is False:
            self._logger.warning("could not change to directory %s", path)
            return []

        if len(pattern) == 0:
            file_list = self._walk_dir(descend)
        else:
            file_list: List[str] = []
            for entry in self._walk_dir(descend):
                file_name = entry.split(lc.PATH_SEP)[-1]
                if re.match(pattern, file_name):
                    file_list.append(entry)
        return file_list

    def read_data_path(self, path: str) -> Union[bool, int, float, str, None]:
        """
        Read values from control via data path. Only works on iTNC controls.
        For ease of use, the path is formatted by replacing / by \\ and " by '.
        Returns data value read from control formatted in nativ data type or None if reading
        was not successful.
        Requires access level ``DATA`` to work.

        :param path: data path from which to read the value.

        :raises LSV2ProtocolException: if data type could not be determiend
        """
        if not self.versions.is_itnc():
            self._logger.warning("Reading values from data path does not work on non iTNC controls!")
            return None

        path = path.replace("/", lc.PATH_SEP).replace('"', "'")

        if not self.login(lc.Login.DATA):
            self._logger.warning("clould not log in as user DATA")
            return None

        payload = bytearray()
        payload.extend(b"\x00")  # <- ???
        payload.extend(b"\x00")  # <- ???
        payload.extend(b"\x00")  # <- ???
        payload.extend(b"\x00")  # <- ???
        payload.extend(lm.ustr_to_ba(path))

        result = self._send_recive(lc.CMD.R_DP, payload, lc.RSP.S_DP)

        if isinstance(result, (bytearray,)) and len(result) > 0:
            value_type = struct.unpack("!L", result[0:4])[0]
            if value_type == 2:
                data_value = struct.unpack("!h", result[4:6])[0]
            elif value_type == 3:
                data_value = struct.unpack("!l", result[4:8])[0]
            elif value_type == 5:
                data_value = struct.unpack("<d", result[4:12])[0]
            elif value_type == 8:
                data_value = lm.ba_to_ustr(result[4:])
            elif value_type == 11:
                data_value = struct.unpack("!?", result[4:5])[0]
            elif value_type == 16:
                data_value = struct.unpack("!b", result[4:5])[0]
            elif value_type == 17:
                data_value = struct.unpack("!B", result[4:5])[0]
            else:
                raise LSV2ProtocolException("unknown return type: %d for %s" % (value_type, result[4:]))

            self._logger.info("successfully read data path: %s and got value '%s'", path, data_value)
            return data_value

        if self.last_error.e_code == lc.LSV2StatusCode.T_ER_WRONG_PARA:
            self._logger.warning("the argument '%s' is not supported by this control", path)
            return None

        self._logger.warning(
            "an error occurred while querying data path '%s'. Error code was %d",
            path,
            self.last_error.e_code,
        )
        return None

    def axes_location(self) -> Union[Dict[str, float], None]:
        """
        Read axes location from control. Not fully documented, value of first byte unknown.
        Requires access level ``DNC`` to work.
        Returns ``None`` if no data was received or dictionary with key = axis name, value = position

        :raises LSV2DataException: Error during parsing of data values
        """
        if not self.login(lc.Login.DNC):
            self._logger.warning("clould not log in as user DNC")
            return None

        payload = bytearray()
        payload.extend(struct.pack("!H", lc.ParRRI.AXIS_LOCATION))

        result = self._send_recive(lc.CMD.R_RI, payload, lc.RSP.S_RI)
        if isinstance(result, (bytearray,)) and len(result) > 0:
            axes_values = lm.decode_axis_location(result)
            self._logger.info("successfully read axes values: %s", axes_values)
            return axes_values

        self._logger.warning("an error occurred while querying axes position")
        return None

    def grab_screen_dump(self, image_path: pathlib.Path) -> bool:
        """
        Create screen_dump of current control screen and save it as bitmap.
        Requires access level ``DNC`` to work.
        Returns ``True`` if completed successfully.

        :param image_path: path of bmp file for screendump
        """
        if not self.login(lc.Login.FILETRANSFER):
            self._logger.warning("clould not log in as user FILE")
            return False

        temp_file_path = lc.DriveName.TNC + lc.PATH_SEP + "screendump_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".bmp"

        payload = bytearray(struct.pack("!H", lc.ParCCC.SCREENDUMP))
        payload.extend(lm.ustr_to_ba(temp_file_path))

        result = self._send_recive(lc.CMD.C_CC, payload, lc.RSP.T_OK)

        if not (isinstance(result, (bool,)) and result is True):
            self._logger.warning("screen dump was not created")
            return False

        if not self.recive_file(remote_path=temp_file_path, local_path=image_path, binary_mode=True):
            self._logger.warning("could not download screen dump from control")
            return False

        if not self.delete_file(temp_file_path):
            self._logger.warning("clould not delete temporary file on control")
            return False

        self._logger.debug("successfully received screen dump")
        return True

    def get_remote_datetime(self) -> datetime:
        """
        Read current time and date from control
        """
        if not self.login(lc.Login.DIAG):
            self._logger.warning("clould not log in as user for DIAGNOSTICS function")
            return datetime.fromtimestamp(0)

        result = self._send_recive(lc.CMD.R_DT, None, lc.RSP.S_DT)
        if isinstance(result, (bytearray,)) and len(result) > 0:
            ts = lm.decode_timestamp(result)
            self._logger.debug("Time on Control is %s", ts.isoformat())
        else:
            raise LSV2ProtocolException("something went wrong while reading current time and date")
        return ts

    def read_scope_signals(self) -> List[ld.ScopeSignal]:
        """
        Read available scope channels and signals. Only works for iTNC 530.
        Requires access level ``SCOPE`` to work.
        returns list of :py:class:`~pyLSV2.LSV2.ScopeSignal` for each signal
        """
        if not self.versions.is_itnc():
            self._logger.warning("only works for iTNC530")
            return []

        if not self.login(lc.Login.SCOPE):
            self._logger.warning("clould not log in as user for scope function")
            return []

        channel_list: List[ld.ScopeSignal] = []

        content = self._llcom.telegram(lc.CMD.R_OC)
        if self._llcom.last_response in lc.RSP.S_OC:
            channel_list.extend(lms.decode_signal_description(content))

            while True:
                content = self._llcom.telegram(lc.RSP.T_OK)

                if self._llcom.last_response in lc.RSP.S_OC:
                    channel_list.extend(lms.decode_signal_description(content))
                elif self._llcom.last_response in lc.RSP.T_FD:
                    self._logger.info("finished loading and parsing data for all scope signals")
                    break
                else:
                    self._logger.error("something went wrong while reading scope signal")
                    raise LSV2ProtocolException("did not received expected response while reading data for scope signals")

        return channel_list

    def real_time_readings(self, signal_list: List[ld.ScopeSignal], duration: int, interval: int):
        """
        Read signal readings from control in real time. Only works for iTNC 530.
        Before reading data, the signal description is updated with information regardinf offset and factor.
        Requires access level ``SCOPE`` to work.

        :param signal_list: list of :py:class:`~pyLSV2.LSV2.ScopeSignal` which should be read from control
        :param duration: number of seconds for which data should be read
        :param interval: interval in µs between readings

        :raises LSV2ProtocolException:
        """
        if not self.versions.is_itnc():
            self._logger.warning("only works for iTNC530")
            return []

        if not self.login(lc.Login.SCOPE):
            self._logger.warning("clould not log in as user for scope function")
            return []

        self._logger.debug(
            "start recoding %d readings with interval of %d µs",
            duration,
            interval,
        )

        # set interval and select signals
        payload = bytearray()
        payload.extend(struct.pack("!L", interval))
        for signal in signal_list:
            if interval not in [600, 3000, 21000]:
                self._logger.warning("the selected interval doesn't fit for signals readings!")
                raise LSV2ProtocolException("the selected interval must be: 600 or 3000 or 21000 us")
            payload.extend(signal.to_ba())

        result = self._send_recive(lc.CMD.R_OP, payload, lc.RSP.S_OP)
        if isinstance(result, (bytearray,)) and len(result) > 0:
            signal_list = lms.decode_signal_details(signal_list, result)
        else:
            if self.last_error.e_code == 85:
                self._logger.warning("too many signals selected: %d", len(signal_list))
                raise LSV2ProtocolException("too many signals selected???")
            if self.last_error.e_code == lc.LSV2StatusCode.T_ER_OSZI_CHSEL:
                self._logger.warning("Error setting up the channels")
                raise LSV2ProtocolException("Error setting up the channels")
            self._logger.warning("Error while configuring interval and signals")
            raise LSV2ProtocolException("Error while configuring interval and signals")

        # setup trigger and read data from control
        payload = bytearray()
        payload.extend(struct.pack("!H", 6))  # trigger channel?
        payload.extend(struct.pack("!H", 65535))  # trigger mode?
        payload.extend(struct.pack("!L", 0))  # trigger level?
        payload.extend(struct.pack("!L", 0))  # pre trigger?
        payload.extend(struct.pack("!L", interval))

        start = time.time()  # start timer
        recorded_data: List[ld.ScopeReading] = []
        content = self._send_recive(lc.CMD.R_OD, payload, lc.RSP.S_OD)

        if not isinstance(content, (bytearray,)) or len(content) <= 0:
            self._logger.error("something went wrong while reading first data package for signals")
            raise LSV2ProtocolException("something went wrong while reading scope data")

        recorded_data.append(lms.decode_scope_reading(signal_list, content))
        end = time.time()
        timer = end - start
        while timer < duration:
            content = self._llcom.telegram(lc.RSP.T_OK)
            if self._llcom.last_response in lc.RSP.S_OD:
                recorded_data.append(lms.decode_scope_reading(signal_list, content))
                yield recorded_data[0]
            else:
                self._logger.warning("something went wrong during periodically reading scope data, abort reading")
                break
            end = time.time()
            timer = end - start
            recorded_data = []

        self._logger.debug("finished reading scope data")
