#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This library is an attempt to implement the LSV2 communication protocol used by certain
   CNC controls.
   Please consider the dangers of using this library on a production machine! This library is
   by no means complete and could damage the control or cause injuries! Everything beyond simple
   file manipulation is blocked by a lockout parameter. Use at your own risk!
"""
import logging
import re
import struct
from typing import Union
from pathlib import Path

from . import const as lc
from . import misc as lm
from . import translate_messages as lt
from .low_level_com import LLLSV2Com


class LSV2:
    """Implementation of the LSV2 protocol used to communicate with certain CNC controls"""

    def __init__(
        self,
        hostname: str,
        port: int = 0,
        timeout: float = 15.0,
        safe_mode: bool = True,
    ):
        """init object variables and create socket"""
        logging.getLogger(__name__).addHandler(logging.NullHandler())

        self._llcom = LLLSV2Com(hostname, port, timeout)

        self._active_logins = list()

        self.switch_safe_mode(safe_mode)

        self._versions = lm.VersionInfo()
        self._sys_par = lm.SystemParameters()
        self._secure_file_send = False
        self._control_type = lc.ControlType.UNKNOWN

        self._last_lsv2_response = lc.RSP.NONE
        self._last_error_type = -1
        self._last_error_code = lc.LSV2Err.T_ER_NON

    def get_last_error(self) -> tuple:
        """return last error type and code"""
        return (self._last_error_type, self._last_error_code)

    def connect(self):
        """connect to control"""
        self._llcom.connect()
        self._configure_connection()

    def disconnect(self):
        """logout of all open logins and close connection"""
        self.logout(login=None)
        self._llcom.disconnect()
        logging.debug("Connection to host closed")

    def __enter__(self):
        """enter context"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        """exit context"""
        self.disconnect()
        # print(exc_type, exc_value, exc_tb, sep="\n")

    def is_itnc(self) -> bool:
        """return true if control is a iTNC"""
        return self._control_type == lc.ControlType.MILL_OLD

    def is_tnc(self) -> bool:
        """return true if control is a TNC"""
        return self._control_type == lc.ControlType.MILL_NEW

    def is_pilot(self) -> bool:
        """return true if control is a CNCPILOT640"""
        return self._control_type == lc.ControlType.LATHE_NEW

    def switch_safe_mode(self, enable_safe_mode: bool = True):
        """switch between safe mode and unrestricted mode"""
        if enable_safe_mode is False:
            logging.info(
                "disabling safe mode. login and system commands are not restricted. Use with caution!"
            )
            self._known_logins = tuple(e.value for e in lc.Login)
            self._known_sys_cmd = tuple(e.value for e in lc.ParCCC)
        else:
            logging.info("enabling safe mode. restricting functionality")
            self._known_logins = (lc.Login.INSPECT, lc.Login.FILETRANSFER)
            self._known_sys_cmd = (
                lc.ParCCC.SET_BUF1024,
                lc.ParCCC.SET_BUF512,
                lc.ParCCC.SET_BUF2048,
                lc.ParCCC.SET_BUF3072,
                lc.ParCCC.SET_BUF4096,
                lc.ParCCC.SECURE_FILE_SEND,
            )

    def _send_recive(
        self, command: lc.CMD, payload=None, expected_response: lc.RSP = lc.RSP.NONE
    ) -> Union[bool, bytearray]:
        """takes a command and payload, sends it to the control and checks
        if the response is as expected. Returns content if not an error"""

        if payload is None:
            bytes_to_send = bytearray()
        elif isinstance(payload, (bytearray,)):
            bytes_to_send = payload
        else:
            bytes_to_send = bytearray(payload)

        if command is lc.CMD.C_CC:
            if bytes_to_send is None or len(bytes_to_send) != 2:
                logging.warning(
                    "system command requires a payload of at exactly 2 bytes"
                )
                return False

            c_cc_command = struct.unpack("!H", bytes_to_send)[0]
            if c_cc_command not in self._known_sys_cmd:
                logging.debug("unknown or unsupported system command %s", bytes_to_send)
                return False

        self._last_lsv2_response, lsv_content = self._llcom.telegram(
            command, bytes_to_send
        )

        if self._last_lsv2_response is lc.RSP.UNKNOWN:
            # TODO: handle unknown response
            logging.warning("unknown response received")
            return False

        if self._last_lsv2_response is lc.RSP.T_ER:
            # TODO: handle transmission error
            (self._last_error_type, self._last_error_code) = struct.unpack(
                "!BB", lsv_content
            )
            message = lt.get_error_text(self._last_error_type, self._last_error_code)

            logging.warning(
                "error received, type: %d, code: %d '%s'",
                self._last_error_type,
                self._last_error_code,
                message,
            )
            return False

        if self._last_lsv2_response is expected_response:
            # expected response received
            logging.debug("expected response received: %s", self._last_lsv2_response)
            if len(lsv_content) > 0:
                return lsv_content
            return True

        if expected_response is lc.RSP.NONE:
            logging.warning("no response expected")
            # TODO: no response expected
            return False

        # TODO: handle unexpected response
        return False

    def _send_recive_block(
        self,
        command: lc.CMD,
        payload: bytearray,
        expected_response: lc.RSP = lc.RSP.NONE,
    ) -> Union[bool, list]:
        """takes a command and payload, sends it to the control and continues reading
        until the expected response is received."""
        bytes_to_send = payload

        self._last_lsv2_response, lsv_content = self._llcom.telegram(
            command, bytes_to_send
        )

        if self._last_lsv2_response is lc.RSP.UNKNOWN:
            # handle unknown response
            logging.warning("unknown response received")
            return False

        if self._last_lsv2_response is lc.RSP.T_ER:
            # TODO: handle transmission error
            (self._last_error_type, self._last_error_code) = struct.unpack(
                "!BB", lsv_content
            )
            message = lt.get_error_text(self._last_error_type, self._last_error_code)
            logging.error(
                "error received, type: %d, code: %d '%s'",
                self._last_error_type,
                self._last_error_code,
                message,
            )
            return False

        if self._last_lsv2_response in lc.RSP.T_FD:
            if len(lsv_content) > 0:
                logging.error(
                    "transfer should have finished without content but data received: %s",
                    lsv_content,
                )
            else:
                logging.error("transfer finished without content")
            return False

        response_buffer = list()
        if self._last_lsv2_response is expected_response:
            # self._last_lsv2_response is expected_response:
            # expected response received
            logging.debug("expected response received: %s", self._last_lsv2_response)
            while self._last_lsv2_response is expected_response:
                response_buffer.append(lsv_content)
                self._last_lsv2_response, lsv_content = self._llcom.telegram(
                    command=lc.RSP.T_OK
                )
            return response_buffer

        logging.error(
            "received unexpected response %s, with data %s",
            self._last_lsv2_response,
            lsv_content,
        )
        return False

    def _configure_connection(self):
        """Set up the communication parameters for file transfer. Buffer size and secure file
        transfere are enabled based on the capabilitys of the control.

        :rtype: None
        """
        self.login(login=lc.Login.INSPECT)

        self.get_versions()

        self.get_system_parameter()

        logging.info(
            "setting connection settings for %s and block length %s",
            self._versions.control_type,
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
            logging.error(
                "could not decide on a buffer size for maximum message length of %d",
                self._sys_par.max_block_length,
            )
            raise Exception("unknown buffer size")

        if selected_command is None:
            logging.debug("use smallest buffer size of 256")
            self._llcom.set_buffer_size(selected_size)
        else:
            logging.debug("use buffer size of %d", selected_size)
            if self._send_recive(
                lc.CMD.C_CC, struct.pack("!H", selected_command), lc.RSP.T_OK
            ):
                self._llcom.set_buffer_size(selected_size)
            else:
                raise Exception(
                    "error in communication while setting buffer size to %d"
                    % selected_size
                )

        if not self._send_recive(
            lc.CMD.C_CC, struct.pack("!H", lc.ParCCC.SECURE_FILE_SEND), lc.RSP.T_OK
        ):
            logging.info("secure file transfer not supported? use fallback")
            self._secure_file_send = False
        else:
            logging.debug("secure file send is enabled")
            self._secure_file_send = True

        self.login(login=lc.Login.FILETRANSFER)

        logging.info("successfully configured connection parameters and basic logins")

    def login(self, login: lc.Login, password: str = "") -> bool:
        """Request additional access rights. To elevate this level a logon has to be performed. Some levels require a password.

        :param str login: One of the known login strings
        :param str password: optional. Password for login
        :returns: True if execution was successful
        :rtype: bool
        """
        if login in self._active_logins:
            logging.debug("login already active")
            return True

        if login not in self._known_logins:
            logging.error("unknown or unsupported login")
            return False

        payload = bytearray()
        payload.extend(map(ord, login))
        payload.append(0x00)
        if password is not None and len(password) > 0:
            payload.extend(map(ord, password))
            payload.append(0x00)

        if self._send_recive(lc.CMD.A_LG, payload, lc.RSP.T_OK):
            logging.info("login executed successfully for login %s", login)
            self._active_logins.append(login)
            return True

        logging.error("error logging in as %s", login)
        return False

    def logout(self, login=None) -> bool:
        """Drop one or all access right. If no login is supplied all active access rights are dropped.

        :param str login: optional. One of the known login strings
        :returns: True if execution was successful
        :rtype: bool
        """
        payload = bytearray()

        if login is not None:
            if isinstance(login, (lc.Login,)):
                if login in self._active_logins:
                    payload.extend(map(ord, login))
                    payload.append(0x00)
                else:
                    # login is not active
                    return True
            else:
                # unknown login
                return False

        if self._send_recive(lc.CMD.A_LO, payload, lc.RSP.T_OK):
            logging.info("logout executed successfully for login %s", login)
            if login is None:
                self._active_logins = list()
            else:
                self._active_logins.remove(login)
            return True
        return False

    def set_system_command(self, command: lc.ParCCC, parameter: str = ""):
        """
        this function is deprecated!
        Execute a system command on the control if command is one a known value. If safe mode is active, some of the
        commands are disabled. If necessary additinal parameters can be supplied.

        :param int command: system command
        :param str parameter: optional. parameter payload for system command
        :returns: True if execution was successful
        :rtype: bool
        """
        bytes_to_send = bytearray()
        bytes_to_send.extend(struct.pack("!H", command))
        if len(parameter) > 0:
            bytes_to_send.extend(map(ord, parameter))
            bytes_to_send.append(0x00)
        return self._send_recive(lc.CMD.C_CC, bytes_to_send, lc.RSP.T_OK)

    def get_system_parameter(self, force: bool = False) -> lm.SystemParameters:
        """Get all version information, result is bufferd since it is also used internally. With parameter force it is
        possible to manually re-read the information form the control

        :param bool force: if True the information is read even if it is already buffered
        :returns: dictionary with system parameters like number of plc variables, supported lsv2 version etc.
        :rtype: dict
        """
        if self._sys_par.lsv2_version != -1 and force is False:
            logging.debug("version info already in memory, return previous values")
        else:
            result = self._send_recive(lc.CMD.R_PR, None, lc.RSP.S_PR)
            if isinstance(result, (bytearray,)):
                self._sys_par = lm.decode_system_parameters(result)
                logging.debug("got system parameters: %s", self._sys_par)
            else:
                logging.error("an error occurred while querying system parameters")
        return self._sys_par

    def get_versions(self, force=False) -> lm.VersionInfo:
        """Get all version information, result is bufferd since it is also used internally. With parameter force it is
        possible to manually re-read the information form the control

        :param bool force: if True the information is read even if it is already buffered
        :returns: dictionary with version text for control type, nc software, plc software, software options etc.
        :rtype: dict
        """
        if len(self._versions.control_version) > 0 and force is False:
            logging.debug("version info already in memory, return previous values")
        else:
            info_data = lm.VersionInfo()

            result = self._send_recive(
                lc.CMD.R_VR, struct.pack("!B", lc.ParRVR.CONTROL), lc.RSP.S_VR
            )
            if isinstance(result, (bytearray,)) and len(result) > 0:
                info_data.control_version = lm.ba_to_ustr(result)
            else:
                raise Exception("Could not read version information from control")

            if info_data.control_version in ("TNC640", "TNC620", "TNC320", "TNC128"):
                info_data.control_type = lc.ControlType.MILL_NEW
            elif info_data.control_version in ("iTNC530", "iTNC530 Programm"):
                info_data.control_type = lc.ControlType.MILL_OLD
            elif info_data.control_version in ("CNCPILOT640",):
                info_data.control_type = lc.ControlType.LATHE_NEW
            else:
                logging.warning("Unknown control type, treat machine as new style mill")
                info_data.control_type = lc.ControlType.MILL_NEW

            result = self._send_recive(
                lc.CMD.R_VR,
                struct.pack("!B", lc.ParRVR.NC_VERSION),
                lc.RSP.S_VR,
            )
            if isinstance(result, (bytearray,)) and len(result) > 0:
                info_data.nc_version = lm.ba_to_ustr(result)

            result = self._send_recive(
                lc.CMD.R_VR,
                struct.pack("!B", lc.ParRVR.PLC_VERSION),
                lc.RSP.S_VR,
            )
            if isinstance(result, (bytearray,)) and len(result) > 0:
                info_data.plc_version = lm.ba_to_ustr(result)

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
                info_data.id_number= lm.ba_to_ustr(result)

            if self.is_itnc():
                info_data.release_type = "not supported"
            else:
                result = self._send_recive(
                    lc.CMD.R_VR,
                    struct.pack("!B", lc.ParRVR.RELEASE_TYPE),
                    lc.RSP.S_VR,
                )
                if isinstance(result, (bytearray,)) and len(result) > 0:
                    info_data.release_type = lm.ba_to_ustr(result)

            result = self._send_recive(
                lc.CMD.R_VR,
                struct.pack("!B", lc.ParRVR.SPLC_VERSION),
                lc.RSP.S_VR,
            )
            if isinstance(result, (bytearray,)) and len(result) > 0:
                info_data.splc_version = lm.ba_to_ustr(result)
            else:
                info_data.splc_version = "not supported"

            logging.debug("got version info: %s", info_data)
            self._versions = info_data

        return self._versions

    def get_program_status(self) -> lc.PgmState:
        """Get status code of currently active program
        See https://github.com/tfischer73/Eclipse-Plugin-Heidenhain/issues/1

        :returns: status code or False if something went wrong
        :rtype: PgmState
        """
        if self.login(login=lc.Login.DNC):
            payload = struct.pack("!H", lc.ParRRI.PGM_STATE)
            result = self._send_recive(lc.CMD.R_RI, payload, lc.RSP.S_RI)
            if isinstance(result, (bytearray,)):
                logging.debug(
                    "successfully read state of active program: %s",
                    struct.unpack("!H", result)[0],
                )
                return lc.PgmState(struct.unpack("!H", result)[0])
            logging.error("an error occurred while querying program state")
        else:
            logging.error("could not log in as user DNC")
        return lc.PgmState.UNDEFINED

    def get_program_stack(self) -> dict:
        """Get path of currently active nc program(s) and current line number
        See https://github.com/tfischer73/Eclipse-Plugin-Heidenhain/issues/1

        :returns: dictionary with line number, main program and current program or False if something went wrong
        :rtype: dict
        """
        if self.login(login=lc.Login.DNC):
            payload = struct.pack("!H", lc.ParRRI.SELECTED_PGM)
            result = self._send_recive(lc.CMD.R_RI, payload, lc.RSP.S_RI)
            if isinstance(result, (bytearray,)) and len(result) > 0:
                stack_info = lm.decode_stack_info(result)
                logging.debug("successfully read active program stack: %s", stack_info)
                return stack_info
            logging.error("an error occurred while querying active program state")
        else:
            logging.error("could not log in as user DNC")
        return dict()

    def get_execution_status(self) -> lc.ExecState:
        """Get status code of program state to text
        See https://github.com/drunsinn/pyLSV2/issues/1

        :returns: status code or False if something went wrong
        :rtype: ExecState
        """
        if self.login(login=lc.Login.DNC):
            payload = struct.pack("!H", lc.ParRRI.EXEC_STATE)
            result = self._send_recive(lc.CMD.R_RI, payload, lc.RSP.S_RI)
            if isinstance(result, (bytearray,)):
                logging.debug("read execution state %d", struct.unpack("!H", result)[0])
                return lc.ExecState(struct.unpack("!H", result)[0])
            logging.error("an error occurred while querying execution state")
        else:
            logging.error("could not log in as user DNC")
        return lc.ExecState.UNDEFINED

    def get_directory_info(self, remote_directory: str = "") -> dict:
        """Query information a the current working directory on the control

        :param str remote_directory: optional. If set, working directory will be changed
        :returns: dictionary with info about the directory or False if an error occurred
        :rtype: dict
        """
        if self.login(lc.Login.FILETRANSFER):
            if (
                len(remote_directory) > 0
                and self.change_directory(remote_directory) is False
            ):
                logging.error(
                    "could not change current directory to read directory info for %s",
                    remote_directory,
                )
                return dict()
            result = self._send_recive(lc.CMD.R_DI, None, lc.RSP.S_DI)
            if isinstance(result, (bytearray,)) and len(result) > 0:
                dir_info = lm.decode_directory_info(result)
                logging.debug(
                    "successfully received directory information %s", dir_info
                )
                return dir_info
            logging.error("an error occurred while querying directory info")
        else:
            logging.error("could not log in as user FILE")
        return dict()

    def change_directory(self, remote_directory: str) -> bool:
        """Change the current working directoyon the control

        :param str remote_directory: path of directory on the control
        :returns: True if changing of directory succeeded
        :rtype: bool
        """
        if self.login(lc.Login.FILETRANSFER):
            dir_path = remote_directory.replace("/", lc.PATH_SEP)
            payload = bytearray(map(ord, dir_path))
            payload.append(0x00)
            result = self._send_recive(lc.CMD.C_DC, payload, lc.RSP.T_OK)
            if isinstance(result, (bool,)) and result is True:
                logging.debug("changed working directory to %s", dir_path)
                return True
            logging.error("an error occurred while changing directory")
        else:
            logging.error("could not log in as user FILE")
        return False

    def get_file_info(self, remote_file_path: str) -> dict:
        """Query information about a file

        :param str remote_file_path: path of file on the control
        :returns: dictionary with info about file of False if remote path does not exist
        :rtype: dict
        """
        if self.login(lc.Login.FILETRANSFER):
            file_path = remote_file_path.replace("/", lc.PATH_SEP)
            payload = bytearray(map(ord, file_path))
            payload.append(0x00)
            result = self._send_recive(lc.CMD.R_FI, payload, lc.RSP.S_FI)
            if isinstance(result, (bytearray,)) and len(result) > 0:
                file_info = lm.decode_file_system_info(result, self._control_type)
                logging.debug("successfully received file information %s", file_info)
                return file_info
            logging.warning(
                "an error occurred while querying file info this might also indicate that it does not exist %s",
                remote_file_path,
            )
        else:
            logging.error("could not log in as user FILE")
        return dict()

    def get_directory_content(self) -> list:
        """Query content of current working directory from the control.
        In some situations it is necessary to fist call get_directory_info() or else
        the attributes won't be correct.

        :returns: list of dict with info about directory entries
        :rtype: list
        """
        dir_content = list()
        if self.login(lc.Login.FILETRANSFER):
            payload = bytearray(struct.pack("!H", lc.ParRDR.SINGLE))
            result = self._send_recive_block(lc.CMD.R_DR, payload, lc.RSP.S_DR)
            if isinstance(result, (list,)):
                for entry in result:
                    dir_content.append(
                        lm.decode_file_system_info(entry, self._control_type)
                    )
                logging.debug(
                    "successfully received %d packages for directory content %s",
                    len(result),
                    dir_content,
                )
            else:
                logging.error("an error occurred while directory content info")
        else:
            logging.error("could not log in as user FILE")
        return dir_content

    def get_drive_info(self) -> list:
        """Query info all drives and partitions from the control

        :returns: list of dict with with info about drive entries
        :rtype: list
        """
        drives_list = list()
        if self.login(lc.Login.FILETRANSFER):
            payload = bytearray(struct.pack("!H", lc.ParRDR.DRIVES))
            result = self._send_recive_block(lc.CMD.R_DR, payload, lc.RSP.S_DR)
            if isinstance(result, (list,)):
                for entry in result:
                    drives_list.append(entry)
                logging.debug(
                    "successfully received %d packages for drive information %s",
                    len(result),
                    drives_list,
                )
            else:
                logging.error("an error occurred while reading drive info")
        else:
            logging.error("could not log in as user FILE")
        return drives_list

    def make_directory(self, dir_path: str) -> bool:
        """Create a directory on control. If necessary also creates parent directories

        :param str dir_path: path of directory on the control
        :returns: True if creating of directory completed successfully
        :rtype: bool
        """
        path_parts = dir_path.replace("/", lc.PATH_SEP).split(
            lc.PATH_SEP
        )  # convert path
        path_to_check = ""
        for part in path_parts:
            path_to_check += part + lc.PATH_SEP
            # no file info -> does not exist and has to be created
            if len(self.get_file_info(path_to_check)) == 0:
                payload = bytearray()
                payload.extend(map(ord, path_to_check))
                payload.append(0x00)  # terminate string
                result = self._send_recive(lc.CMD.C_DM, payload, lc.RSP.T_OK)
                if isinstance(result, (bool,)) and result is True:
                    logging.debug("Directory created successfully")
                else:
                    logging.error(
                        "an error occurred while creating directory %s", dir_path
                    )
                    return False
            else:
                logging.debug("nothing to do as this segment already exists")
        return True

    def delete_empty_directory(self, dir_path: str) -> bool:
        """Delete empty directory on control

        :param str file_path: path of directory on the control
        :returns: True if deleting of directory completed successfully
        :rtype: bool
        """
        dir_path = dir_path.replace("/", lc.PATH_SEP)
        payload = bytearray(map(ord, dir_path))
        payload.append(0x00)
        result = self._send_recive(lc.CMD.C_DD, payload, lc.RSP.T_OK)
        if isinstance(result, (bool)) and result is True:
            logging.debug("successfully deleted directory %s", dir_path)
            return True
        logging.warning(
            "an error occurred while deleting directory %s, this might also indicate that it it does not exist",
            dir_path,
        )
        return False

    def delete_file(self, file_path: str) -> bool:
        """Delete file on control

        :param str file_path: path of file on the control
        :returns: True if deleting of file completed successfully
        :rtype: bool
        """
        file_path = file_path.replace("/", lc.PATH_SEP)
        payload = bytearray()
        payload.extend(map(ord, file_path))
        payload.append(0x00)
        if not self._send_recive(lc.CMD.C_FD, payload, lc.RSP.T_OK):
            logging.warning(
                "an error occurred while deleting file %s, this might also indicate that it it does not exist",
                file_path,
            )
            return False
        logging.debug("successfully deleted file %s", file_path)
        return True

    def copy_local_file(self, source_path: str, target_path: str) -> bool:
        """Copy file on control from one place to another

        :param str source_path: path of file on the control
        :param str target_path: path of target location
        :returns: True if copying of file completed successfully
        :rtype: bool
        """
        source_path = source_path.replace("/", lc.PATH_SEP)
        target_path = target_path.replace("/", lc.PATH_SEP)

        if lc.PATH_SEP in source_path:
            # change directory
            source_file_name = source_path.split(lc.PATH_SEP)[-1]
            source_directory = source_path.rstrip(source_file_name)
            if not self.change_directory(remote_directory=source_directory):
                raise Exception("could not open the source directory")
        else:
            source_file_name = source_path
            source_directory = "."

        if target_path.endswith(lc.PATH_SEP):
            target_path += source_file_name

        payload = bytearray()
        payload.extend(map(ord, source_file_name))
        payload.append(0x00)
        payload.extend(map(ord, target_path))
        payload.append(0x00)
        logging.debug(
            "prepare to copy file %s from %s to %s",
            source_file_name,
            source_directory,
            target_path,
        )
        if not self._send_recive(lc.CMD.C_FC, payload, lc.RSP.T_OK):
            logging.warning(
                "an error occurred copying file %s to %s", source_path, target_path
            )
            return False
        logging.debug("successfully copied file %s", source_path)
        return True

    def move_local_file(self, source_path: str, target_path: str) -> bool:
        """Move file on control from one place to another

        :param str source_path: path of file on the control
        :param str target_path: path of target location
        :returns: True if moving of file completed successfully
        :rtype: bool
        """
        source_path = source_path.replace("/", lc.PATH_SEP)
        target_path = target_path.replace("/", lc.PATH_SEP)

        if lc.PATH_SEP in source_path:
            source_file_name = source_path.split(lc.PATH_SEP)[-1]
            source_directory = source_path.rstrip(source_file_name)
            if not self.change_directory(remote_directory=source_directory):
                raise Exception("could not open the source directory")
        else:
            source_file_name = source_path
            source_directory = "."

        if target_path.endswith(lc.PATH_SEP):
            target_path += source_file_name

        payload = bytearray()
        payload.extend(map(ord, source_file_name))
        payload.append(0x00)
        payload.extend(map(ord, target_path))
        payload.append(0x00)
        logging.debug(
            "prepare to move file %s from %s to %s",
            source_file_name,
            source_directory,
            target_path,
        )
        if not self._send_recive(lc.CMD.C_FR, payload, lc.RSP.T_OK):
            logging.warning(
                "an error occurred moving file %s to %s", source_path, target_path
            )
            return False
        logging.debug("successfully moved file %s", source_path)
        return True

    def send_file(
        self,
        local_path: Union[str, Path],
        remote_path: str,
        override_file: bool = False,
        binary_mode: bool = False,
    ) -> bool:
        """Upload a file to control

        :param str remote_path: path of file on the control
        :param str local_path: local path of destination with or without file name
        :param bool override_file: flag if file should be replaced if it already exists
        :param bool binary_mode: flag if binary transfer mode should be used, if not set the
                                 file name is checked for known binary file type
        :returns: True if transfer completed successfully
        :rtype: bool
        """
        if isinstance(local_path, (str,)):
            local_file = Path(local_path)
        else:
            local_file = local_path

        if not local_file.is_file():
            logging.error("the supplied path %s did not resolve to a file", local_file)
            raise Exception("local file does not exist! {}".format(local_file))

        remote_path = remote_path.replace("/", lc.PATH_SEP)

        if lc.PATH_SEP in remote_path:
            if remote_path.endswith(lc.PATH_SEP):  # no filename given
                remote_file_name = local_file.name
                remote_directory = remote_path
            else:
                remote_file_name = remote_path.split(lc.PATH_SEP)[-1]
                remote_directory = remote_path.rstrip(remote_file_name)
                if not self.change_directory(remote_directory=remote_directory):
                    raise Exception(
                        "could not open the source directory {}".format(
                            remote_directory
                        )
                    )
        else:
            remote_file_name = remote_path
            remote_directory = self.get_directory_info()["Path"]  # get pwd
        remote_directory = remote_directory.rstrip(lc.PATH_SEP)

        if not self.get_directory_info(remote_directory):
            logging.debug("remote path does not exist, create directory(s)")
            self.make_directory(remote_directory)

        remote_info = self.get_file_info(
            remote_directory + lc.PATH_SEP + remote_file_name
        )

        if remote_info:
            logging.debug("remote path exists and points to file's")
            if override_file:
                if not self.delete_file(
                    remote_directory + lc.PATH_SEP + remote_file_name
                ):
                    raise Exception(
                        "something went wrong while deleting file {}".format(
                            remote_directory + lc.PATH_SEP + remote_file_name
                        )
                    )
            else:
                logging.warning("remote file already exists, override was not set")
                return False

        logging.debug(
            "ready to send file from %s to %s",
            local_file,
            remote_directory + lc.PATH_SEP + remote_file_name,
        )

        payload = bytearray()
        payload.extend(map(ord, remote_directory + lc.PATH_SEP + remote_file_name))
        payload.append(0x00)
        if binary_mode or lm.is_file_binary(local_path):
            payload.append(lc.MODE_BINARY)
            logging.info("selecting binary transfer mode for this file type")
        else:
            payload.append(0x00)
            logging.info("selecting non binary transfer mode")

        response, content = self._llcom.telegram(
            lc.CMD.C_FL,
            payload,
        )

        if response in lc.RSP.T_OK:
            with local_file.open("rb") as input_buffer:
                while True:
                    # use current buffer size but reduce by 10 to make sure it fits together with command and size
                    buffer = bytearray(
                        input_buffer.read(self._llcom.get_buffer_size() - 8 - 2)
                    )
                    if not buffer:
                        # finished reading file
                        break

                    response, content = self._llcom.telegram(
                        lc.RSP.S_FL,
                        buffer,
                    )
                    if response in lc.RSP.T_OK:
                        pass
                    else:
                        if response in lc.RSP.T_ER:
                            (
                                self._last_error_type,
                                self._last_error_code,
                            ) = struct.unpack("!BB", content)
                            message = lt.get_error_text(
                                self._last_error_type, self._last_error_code
                            )
                            logging.warning(
                                "error received, type: %d, code: %d '%s'",
                                self._last_error_type,
                                self._last_error_code,
                                message,
                            )
                        else:
                            logging.error("could not send data with error %s", response)
                        return False

            # signal that no more data is being sent
            if self._secure_file_send:
                if not self._send_recive(lc.CMD.T_FD, None, lc.RSP.T_OK):
                    logging.error("could not send end of file with error")
                    return False
            else:
                if not self._send_recive(lc.CMD.T_FD, None, lc.RSP.NONE):
                    logging.error("could not send end of file with error")
                    return False

        else:
            if response in lc.RSP.T_ER:
                self._last_error_type, self._last_error_code = struct.unpack(
                    "!BB", content
                )
                message = lt.get_error_text(
                    self._last_error_type, self._last_error_code
                )
                logging.warning(
                    "error received, type: %d, code: %d '%s'",
                    self._last_error_type,
                    self._last_error_code,
                    message,
                )
            else:
                logging.error("could not send file with error %s", response)
            return False

        return True

    def recive_file(
        self,
        remote_path: str,
        local_path: Union[str, Path],
        override_file: bool = False,
        binary_mode: bool = False,
    ) -> bool:
        """Download a file from control

        :param str remote_path: path of file on the control
        :param str local_path: local path of destination with or without file name
        :param bool override_file: flag if file should be replaced if it already exists
        :param bool binary_mode: flag if binary transfer mode should be used, if not set the file name is
                                 checked for known binary file type
        :returns: True if transfer completed successfully
        :rtype: bool
        """
        if isinstance(local_path, (str,)):
            local_file = Path(local_path)
        else:
            local_file = local_path

        remote_path = remote_path.replace("/", lc.PATH_SEP)
        remote_file_info = self.get_file_info(remote_path)
        if not remote_file_info:
            logging.error("remote file does not exist: %s", remote_path)
            return False

        if local_file.is_dir():
            local_file.joinpath(remote_path.split("/")[-1])

        if local_file.is_file():
            logging.debug("local path exists and points to file")
            if override_file:
                local_file.unlink()
            else:
                logging.warning(
                    "local file already exists and override was not set. doing nothing"
                )
                return False

        logging.debug("loading file from %s to %s", remote_path, local_file)

        payload = bytearray()
        payload.extend(map(ord, remote_path))
        payload.append(0x00)
        if binary_mode or lm.is_file_binary(remote_path):
            payload.append(lc.MODE_BINARY)  # force binary transfer
            logging.info("using binary transfer mode")
        else:
            payload.append(0x00)
            logging.info("using non binary transfer mode")

        response, content = self._llcom.telegram(
            lc.CMD.R_FL,
            payload,
        )

        with local_file.open("wb") as out_file:
            if response in lc.RSP.S_FL:
                if binary_mode:
                    out_file.write(content)
                else:
                    out_file.write(content.replace(b"\x00", b"\r\n"))
                logging.debug("received first block of file file %s", remote_path)

                while True:
                    response, content = self._llcom.telegram(
                        lc.RSP.T_OK,
                    )
                    if response in lc.RSP.S_FL:
                        if binary_mode:
                            out_file.write(content)
                        else:
                            out_file.write(content.replace(b"\x00", b"\r\n"))
                        logging.debug("received %d more bytes for file", len(content))
                    elif response in lc.RSP.T_FD:
                        logging.info("finished loading file")
                        break
                    else:
                        if response in lc.RSP.T_ER or response in lc.RSP.T_BD:
                            (
                                self._last_error_type,
                                self._last_error_code,
                            ) = struct.unpack("!BB", content)
                            message = lt.get_error_text(
                                self._last_error_type, self._last_error_code
                            )
                            logging.error(
                                "an error occurred while loading the first block of data for file %s, type: %d, code: %d '%s'",
                                remote_path,
                                self._last_error_type,
                                self._last_error_code,
                                message,
                            )
                        else:
                            logging.error(
                                "something went wrong while receiving file data %s",
                                remote_path,
                            )
                        return False
            else:
                if response in lc.RSP.T_ER or response in lc.RSP.T_BD:
                    self._last_error_type, self._last_error_code = struct.unpack(
                        "!BB", content
                    )
                    message = lt.get_error_text(
                        self._last_error_type, self._last_error_code
                    )
                    logging.error(
                        "an error occurred while loading the first block of data for file %s, type: %d, code: %d '%s'",
                        remote_path,
                        self._last_error_type,
                        self._last_error_code,
                        message,
                    )
                else:
                    logging.error("could not load file with error %s", response)
                    self._last_error_code = None
                return False

        logging.info(
            "received %d bytes transfer complete for file %s to %s",
            local_file.stat().st_size,
            remote_path,
            local_file,
        )

        return True

    def read_plc_memory(
        self, address: int, mem_type: lc.MemoryType, count: int = 1
    ) -> list:
        """Read data from plc memory.

        :param address: which memory location should be read, starts at 0 up to the max number for each type
        :param mem_type: what datatype to read
        :param count: how many elements should be read at a time, from 1 (default) up to 255 or max number
        :returns: a list with the data values
        :raises Exception: raises an Exception
        """

        if self._sys_par.lsv2_version != -1:
            self.get_system_parameter()

        if not self.login(login=lc.Login.PLCDEBUG):
            logging.error("could not log in as user PLCDEBUG")
            return list()

        if count > 0xFF:
            logging.error("can't read more than 255 elements at a time")
            return list()

        if mem_type is lc.MemoryType.MARKER:
            start_address = self._sys_par.markers_start_address
            max_count = self._sys_par.number_of_markers
            mem_byte_count = 1
            unpack_string = "!?"
        elif mem_type is lc.MemoryType.INPUT:
            start_address = self._sys_par.inputs_start_address
            max_count = self._sys_par.number_of_inputs
            mem_byte_count = 1
            unpack_string = "!?"
        elif mem_type is lc.MemoryType.OUTPUT:
            start_address = self._sys_par.outputs_start_address
            max_count = self._sys_par.number_of_outputs
            mem_byte_count = 1
            unpack_string = "!?"
        elif mem_type is lc.MemoryType.COUNTER:
            start_address = self._sys_par.counters_start_address
            max_count = self._sys_par.number_of_counters
            mem_byte_count = 1
            unpack_string = "!?"
        elif mem_type is lc.MemoryType.TIMER:
            start_address = self._sys_par.timers_start_address
            max_count = self._sys_par.number_of_timers
            mem_byte_count = 1
            unpack_string = "!?"
        elif mem_type is lc.MemoryType.BYTE:
            start_address = self._sys_par.words_start_address
            max_count = self._sys_par.number_of_words * 2
            mem_byte_count = 1
            unpack_string = "!B"
        elif mem_type is lc.MemoryType.WORD:
            start_address = self._sys_par.words_start_address
            max_count = self._sys_par.number_of_words
            mem_byte_count = 2
            unpack_string = "<H"
        elif mem_type is lc.MemoryType.DWORD:
            start_address = self._sys_par.words_start_address
            max_count = self._sys_par.number_of_words / 4
            mem_byte_count = 4
            unpack_string = "<L"
        elif mem_type is lc.MemoryType.STRING:
            start_address = self._sys_par.strings_start_address
            max_count = self._sys_par.number_of_strings
            mem_byte_count = self._sys_par.max_string_lenght
            unpack_string = "{}s".format(mem_byte_count)
        elif mem_type is lc.MemoryType.INPUT_WORD:
            start_address = self._sys_par.input_words_start_address
            max_count = self._sys_par.number_of_input_words
            mem_byte_count = 2
            unpack_string = "<H"
        else:  # mem_type is lc.MemoryType.OUTPUT_WORD:
            start_address = self._sys_par.output_words_start_address
            max_count = self._sys_par.number_of_output_words
            mem_byte_count = 2
            unpack_string = "<H"

        if count > max_count:
            logging.error("maximum number of values is %d", max_count)
            return list()

        plc_values = list()

        if mem_type is lc.MemoryType.STRING:
            # advance address if necessary
            address = address + (count - 1) * mem_byte_count
            for i in range(count):
                payload = bytearray()
                payload.extend(
                    struct.pack("!L", start_address + address + i * mem_byte_count)
                )
                payload.extend(struct.pack("!B", mem_byte_count))
                result = self._send_recive(lc.CMD.R_MB, payload, lc.RSP.S_MB)
                if isinstance(result, (bytearray,)) and len(result) > 0:
                    logging.debug("read string %d", address + i * mem_byte_count)
                    plc_values.append(
                        struct.unpack(unpack_string, result)[0]
                        .rstrip(b"\x00")
                        .decode("utf8")
                    )
                else:
                    logging.error(
                        "failed to read string from address %d",
                        start_address + address + i * mem_byte_count,
                    )
                    return list()
        else:
            payload = bytearray()
            payload.extend(struct.pack("!L", start_address + address))
            payload.extend(struct.pack("!B", count * mem_byte_count))
            result = self._send_recive(lc.CMD.R_MB, payload, lc.RSP.S_MB)
            if isinstance(result, (bytearray,)) and len(result) > 0:
                logging.debug("read %d value(s) from address %d", count, address)
                for i in range(0, len(result), mem_byte_count):
                    plc_values.append(
                        struct.unpack(unpack_string, result[i : i + mem_byte_count])[0]
                    )
            else:
                logging.error(
                    "failed to read string from address %d", start_address + address
                )
                return list()

        return plc_values

    def set_keyboard_access(self, unlocked: bool) -> bool:
        """Enable or disable the keyboard on the control. Requires access level MONITOR to work.

        :param bool unlocked: if True unlocks the keyboard. if false, input is set to locked
        :returns: True or False if command was executed successfully
        :rtype: bool
        """

        payload = bytearray()
        if unlocked:
            payload.extend(struct.pack("!B", 0x00))
        else:
            payload.extend(struct.pack("!B", 0x01))

        result = self._send_recive(lc.CMD.C_LK, payload, lc.RSP.T_OK)
        if result:
            if unlocked:
                logging.debug("command to unlock keyboard was successful")
            else:
                logging.debug("command to lock keyboard was successful")
            return True
        else:
            logging.warning("an error occurred changing the state of the keyboard lock")
        return False

    def get_machine_parameter(self, name: str) -> str:
        """Read machine parameter from control. Requires access INSPECT level to work.

        :param str name: name of the machine parameter. For iTNC the parameter number hase to be converted to string
        :returns: value of parameter or empty string if command not successful
        :rtype: str
        """
        payload = bytearray()
        payload.extend(map(ord, name))
        payload.append(0x00)
        result = self._send_recive(lc.CMD.R_MC, payload, lc.RSP.S_MC)
        if isinstance(result, (bytearray,)) and len(result) > 0:
            value = lm.ba_to_ustr(result)
            logging.debug("machine parameter %s has value %s", name, value)
            return value

        logging.warning("an error occurred while reading machine parameter %s", name)
        return ""

    def set_machine_parameter(self, name: str, value: str, safe_to_disk=False) -> bool:
        """Set machine parameter on control. Requires access PLCDEBUG level to work.
           Writing a parameter takes some time, make sure to set timeout sufficiently high!

        :param str name: name of the machine parameter. For iTNC the parameter number hase to be converted to string
        :param str value: new value of the machine parameter. There is no type checking, if the value can not be converted by the control an error will be sent.
        :param bool safe_to_disk: If True the new value will be written to the harddisk and stay permanent. If False (default) the value will only be available until the next reboot.

        :returns: True or False if command was executed successfully
        :rtype: bool
        """
        payload = bytearray()
        if safe_to_disk:
            payload.extend(struct.pack("!L", 0x00))
        else:
            payload.extend(struct.pack("!L", 0x01))
        payload.extend(map(ord, name))
        payload.append(0x00)
        payload.extend(map(ord, value))
        payload.append(0x00)

        result = self._send_recive(lc.CMD.C_MC, payload, lc.RSP.T_OK)
        if result:
            logging.debug(
                "setting of machine parameter %s to value %s was successful",
                name,
                value,
            )
            return True

        logging.warning(
            "an error occurred while setting machine parameter %s to value %s",
            name,
            value,
        )
        return False

    def send_key_code(self, key_code: Union[lc.KeyCode, lc.OldKeyCode]) -> bool:
        """Send key code to control. Behaves as if the associated key was pressed on the
           keyboard. Requires access MONITOR level to work. To work correctly you first
           have to lock the keyboard and unlock it afterwards!:

           set_keyboard_access(False)
           send_key_code(KeyCode.CE)
           set_keyboard_access(True)

        :param int key_code: code number of the keyboard key

        :returns: True or False if command was executed successfully
        :rtype: bool
        """
        payload = bytearray()
        payload.extend(struct.pack("!H", key_code))

        result = self._send_recive(lc.CMD.C_EK, payload, lc.RSP.T_OK)
        if result:
            logging.debug("sending the key code %d was successful", key_code)
            return True

        logging.warning("an error occurred while sending the key code %d", key_code)
        return False

    def get_spindle_tool_status(self) -> dict:
        """Get information about the tool currently in the spindle

        :returns: tool information or False if something went wrong
        :rtype: dict
        """
        self.login(login=lc.Login.DNC)
        payload = bytearray()
        payload.extend(struct.pack("!H", lc.ParRRI.CURRENT_TOOL))
        result = self._send_recive(lc.CMD.R_RI, payload, lc.RSP.S_RI)
        if isinstance(result, (bytearray,)) and len(result) > 0:
            tool_info = lm.decode_tool_information(result)
            logging.debug("successfully read info on current tool: %s", tool_info)
            return tool_info
        logging.warning(
            "an error occurred while querying current tool information. This does not work for all control types"
        )
        return dict()

    def get_override_info(self) -> dict:
        """Get information about the override info

        :returns: override information or False if something went wrong
        :rtype: dict
        """
        self.login(login=lc.Login.DNC)
        payload = bytearray()
        payload.extend(struct.pack("!H", lc.ParRRI.OVERRIDE))
        result = self._send_recive(lc.CMD.R_RI, payload, lc.RSP.S_RI)
        if isinstance(result, (bytearray,)) and len(result) > 0:
            override_info = lm.decode_override_information(result)
            logging.debug("successfully read override info: %s", override_info)
            return override_info
        logging.warning(
            "an error occurred while querying current override information. This does not work for all control types"
        )
        return dict()

    def get_error_messages(self) -> list:
        """Get information about the first or next error displayed on the control

        :param bool next_error: if True check if any further error messages are available
        :returns: error information or False if something went wrong
        :rtype: dict
        """
        messages = list()
        self.login(login=lc.Login.DNC)

        payload = bytearray()
        payload.extend(struct.pack("!H", lc.ParRRI.FIRST_ERROR))
        result = self._send_recive(lc.CMD.R_RI, payload, lc.RSP.S_RI)
        if isinstance(result, (bytearray,)) and len(result) > 0:
            messages.append(lm.decode_error_message(result))
            payload = bytearray()
            payload.extend(struct.pack("!H", lc.ParRRI.NEXT_ERROR))
            result = self._send_recive(lc.CMD.R_RI, payload, lc.RSP.S_RI)
            logging.debug("successfully read first error but further errors")

            while isinstance(result, (bytearray,)):
                messages.append(lm.decode_error_message(result))
                result = self._send_recive(lc.CMD.R_RI, payload, lc.RSP.S_RI)

            if self._last_error_code == lc.LSV2Err.T_ER_NO_NEXT_ERROR:
                logging.debug("successfully read all errors")
            else:
                logging.warning("an error occurred while querying error information.")

            return messages

        elif self._last_error_code == lc.LSV2Err.T_ER_NO_NEXT_ERROR:
            logging.debug("successfully read first error but no error active")
            return messages

        logging.warning(
            "an error occurred while querying error information. This does not work for all control types"
        )

        return list()

    def _walk_dir(self, descend=True) -> list:
        """helber function to recursively search in directories for files

        :param bool descend: control if search should run recursively
        :returns: list of files found in directory
        :rtype: list
        """
        current_path = self.get_directory_info()["Path"]
        content = list()
        for entry in self.get_directory_content():
            if (
                entry["Name"] == "."
                or entry["Name"] == ".."
                or entry["Name"].endswith(":")
            ):
                continue
            current_fs_element = str(current_path + entry["Name"]).replace("/", PATH_SEP)
            if entry["is_directory"] is True and descend is True:
                if self.change_directory(current_fs_element):
                    content.extend(self._walk_dir())
            else:
                content.append(current_fs_element)
        self.change_directory(current_path)
        return content

    def get_file_list(
        self, path: str = "", descend: bool = True, pattern: str = ""
    ) -> list:
        """Get list of files in directory structure.

        :param str path: path of the directory where files should be searched. if None than the current directory is used
        :param bool descend: control if search should run recursiv
        :param str pattern: regex string to filter the file names
        :returns: list of files found in directory
        :rtype: list
        """
        if path is not None:
            if self.change_directory(path) is False:
                logging.warning("could not change to directory")
                return list()

        if pattern is None:
            file_list = self._walk_dir(descend)
        else:
            file_list = list()
            for entry in self._walk_dir(descend):
                file_name = entry.split(lc.PATH_SEP)[-1]
                if re.match(pattern, file_name):
                    file_list.append(entry)
        return file_list

    def read_data_path(self, path: str):
        """Read values from control via data path. Only works on iTNC controls.
        For ease of use, the path is formatted by replacing / by \\ and " by '.

        :param str path: data path from which to read the value.
        :returns: data value read from control formatted in nativ data type or None if reading was not successful
        """
        if not self.is_itnc():
            logging.warning(
                "Reading values from data path does not work on non iTNC controls!"
            )

        path = path.replace("/", lc.PATH_SEP).replace('"', "'")

        self.login(login=lc.Login.DATA)

        payload = bytearray()
        payload.extend(b"\x00")  # <- ???
        payload.extend(b"\x00")  # <- ???
        payload.extend(b"\x00")  # <- ???
        payload.extend(b"\x00")  # <- ???
        payload.extend(map(ord, path))
        payload.append(0x00)  # escape string

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
                data_value = result[4:].strip(b"\x00").decode("utf-8")
            elif value_type == 11:
                data_value = struct.unpack("!?", result[4:5])[0]
            elif value_type == 16:
                data_value = struct.unpack("!b", result[4:5])[0]
            elif value_type == 17:
                data_value = struct.unpack("!B", result[4:5])[0]
            else:
                raise Exception(
                    "unknown return type: %d for %s" % (value_type, result[4:])
                )

            logging.info(
                'successfuly read data path: %s and got value "%s"', path, data_value
            )
            return data_value
        logging.warning(
            'an error occurred while querying data path "%s". This does not work for all control types',
            path,
        )
        return None

    def get_axes_location(self) -> dict:
        """Read axes location from control. Not fully documented, value of first byte unknown.
        - only tested on TNC640 programming station

        :returns: dictionary of axis label and current value
        """
        self.login(login=lc.Login.DNC)

        payload = bytearray()
        payload.extend(struct.pack("!H", lc.ParRRI.AXIS_LOCATION))

        result = self._send_recive(lc.CMD.R_RI, payload, lc.RSP.S_RI)
        if isinstance(result, (bytearray,)) and len(result) > 0:
            # unknown = result[0:1] # <- ???
            number_of_axes = struct.unpack("!b", result[1:2])[0]

            split_list = list()
            beginning = 2
            for i, byte in enumerate(result[beginning:]):
                if byte == 0x00:
                    value = result[beginning : i + 3]
                    split_list.append(value.strip(b"\x00").decode("utf-8"))
                    beginning = i + 3

            if len(split_list) != (2 * number_of_axes):
                raise Exception("error parsing axis values")

            axes_values = dict()
            for i in range(number_of_axes):
                axes_values[split_list[i + number_of_axes]] = float(split_list[i])

            logging.info("successfully read axes values: %s", axes_values)

            return axes_values

        logging.error("an error occurred while querying axes position")
        return dict()
