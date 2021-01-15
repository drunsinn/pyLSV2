#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Python 3 LSV2 library
   This library is an attempt to implement the LSV2 communication protocol used by certain
   CNC controls. It's goal is to transfer file between the application and the control as well
   as collect information about said files.
   Most of this library is based on the work of tfischer73 and his Eclipse
   plugin https://github.com/tfischer73/Eclipse-Plugin-Heidenhain . Since I could not find any
   documentation beside the plugin some parts are based on re-engineering and might therefore be
   not correct.
   Everything related to PLC or unknown/untested System functions was left out as these function
   might compromise the control.
"""
import struct
import logging
import datetime
from pathlib import Path
from .translate_error import get_error_text
from .low_level_com import LLLSV2Com


class LSV2():
    """Implementation of the LSV2 protocol used to communicate with certain CNC controls.
       This is just a test implementation that will get worked into a complete Python library. It
       has only been tested with a programming station for the TNC 640 with software version
       340595 8 SP1.
       No tests on real machines have been made so far!"""

    DRIVE_TNC = 'TNC:'
    DRIVE_TNC = 'PLC:'
    DRIVE_LOG = 'LOG:'

    BIN_FILES = ('.ads', '.bak', '.bck', '.bin', '.bmp', '.bmx', '.chm', '.cyc', '.cy%',
        '.dmp', '.dll', '.eak', '.elf', '.enc', '.exe', '.gds', '.gif', '.hbi', '.he', '.ioc',
        '.iocp', '.jpg', '.jpeg', '.map', '.mds', '.mo', '.omf', '.pdf', '.png', '.pyc', '.s',
        '.sds', '.sk', '.str', '.xml', '.xls', '.xrs', '.zip')

    # const for login
    LOGIN_INSPECT = 'INSPECT'  # nur lesende Funktionen ausführbar
    LOGIN_DIAG = 'DIAGNOSTICS'  # Logbuch / Recover
    LOGIN_PLCDEBUG = 'PLCDEBUG'  # Schreibender PLC
    LOGIN_FILETRANSFER = 'FILE'  # Dateisystem
    LOGIN_MONITOR = 'MONITOR'  # TNC Fernbedienung und Screendump
    LOGIN_DSP = 'DSP'  # DSP Funktionen
    LOGIN_DNC = 'DNC'  # DNC-Funktionen
    LOGIN_SCOPE = 'OSZI'  # Remote Scope
    LOGIN_STREAMAXES = 'STREAMAXES'  # Streamen von Achsdaten
    LOGIN_FILEPLC = 'FILEPLC'  # Dateisystem mit Zugriff auf PLC:-Drive, Passwort notwendig
    LOGIN_FILESYS = 'FILESYS'  # Dateisystem mit Zugriff auf PLC:-Drive, Passwort notwendig

    # known lsv2 telegrams
    # A_LG: used to gain access to certain parts of the control, followed by a logon name and an optional password
    COMMAND_A_LG = 'A_LG'
    # A_LO: used to drop access to certain parts of the control, followed by an optional logon name
    COMMAND_A_LO = 'A_LO'
    # C_CC: used to set system commands
    COMMAND_C_CC = 'C_CC'
    # C_DC: change the working directory for future file operations, followed by a null terminated string
    COMMAND_C_DC = 'C_DC'

    # C_DS: found via bruteforce test, purpose unknown!
    # COMMAND_C_DS = 'C_DS'

    # C_DD: delete a directory, followed by a null terminated string
    COMMAND_C_DD = 'C_DD'
    # C_DM: create a new directory, followed by a null terminated string
    COMMAND_C_DM = 'C_DM'

    # C_EK: found via bruteforce test, purpose unknown!
    # COMMAND_C_EK = 'C_EK'
    # C_FA: found via bruteforce test, purpose unknown!
    # COMMAND_C_FA = 'C_FA'

    # C_FC: ocal file copy from current directory, filename + null + target path + null, found via wireshark
    COMMAND_C_FC = 'C_FC'
    # C_FD: delete a file, followed by a null terminated string
    COMMAND_C_FD = 'C_FD'
    # C_FL: send a file to the control, followed by a null terminated with the filename string
    COMMAND_C_FL = 'C_FL'
    # C_FR: move local file from current directory, filename + null + target path + null, found via wireshark
    COMMAND_C_FR = 'C_FR'

    # COMMAND_C_GC = 'C_GC' # found via bruteforce test, purpose unknown!
    # COMMAND_C_LK = 'C_LK' # found via bruteforce test, purpose unknown!
    # COMMAND_C_MB = 'C_MB' # found via bruteforce test, purpose unknown!
    # COMMAND_C_MC = 'C_MC' # found via bruteforce test, purpose unknown! -> Timeout and Control hangs!
    # COMMAND_C_OP = 'C_OP' # found via bruteforce test, purpose unknown! -> Timeout
    # COMMAND_C_ST = 'C_ST' # found via bruteforce test, purpose unknown!
    # COMMAND_C_TP = 'C_TP' # found via bruteforce test, purpose unknown!
    # COMMAND_R_CI = 'R_CI' # found via bruteforce test, purpose unknown!

    # R_DI: directory info - read info about the selected directory
    COMMAND_R_DI = 'R_DI'
    # R_DR: get info about directory content
    COMMAND_R_DR = 'R_DR'

    # COMMAND_R_DS = 'R_DS' # found via bruteforce test, purpose unknown!
    # COMMAND_R_DT = 'R_DT' # found via bruteforce test, purpose unknown!

    # R_FI: file info - read info about a file, followed by a null terminated string
    COMMAND_R_FI = 'R_FI'
    # R_FL: load a file from the control, followed by a null terminated with the filename string
    COMMAND_R_FL = 'R_FL'

    # COMMAND_R_IN = 'R_IN' # found via bruteforce test, purpose unknown!
    # COMMAND_R_MB = 'R_MB' # found via bruteforce test, purpose unknown!
    # COMMAND_R_MC = 'R_MC' # found via bruteforce test, purpose unknown!
    # COMMAND_R_OC = 'R_OC' # found via bruteforce test, purpose unknown!
    # COMMAND_R_OD = 'R_OD' # found via bruteforce test, purpose unknown!
    # COMMAND_R_OH = 'R_OH' # found via bruteforce test, purpose unknown!
    # COMMAND_R_OI = 'R_OI' # found via bruteforce test, purpose unknown!

    # R_PR: read parameter from the control
    COMMAND_R_PR = 'R_PR'
    # R_RI: read info about the current state of the control ???, followed by a 16bit number to select which information (20 - 26??)
    COMMAND_R_RI = 'R_RI'

    # COMMAND_R_ST = 'R_ST' # found via bruteforce test, purpose unknown!

    # R_VR: read general info about the control itself
    COMMAND_R_VR = 'R_VR'

    # known lsv2 responses
    # T_OK: signals that the last transaction was completed, no additional data is sent?
    RESPONSE_T_OK = 'T_OK'
    # T_ER: signals that An error occurred during the last transaction, followed by An error code?
    RESPONSE_T_ER = 'T_ER'
    # T_FD: signals that all file data has been sent and the transfer is finished
    RESPONSE_T_FD = 'T_FD'
    # T_BD: signals that An error occurred during the file transfer, it is followed by more data
    RESPONSE_T_BD = 'T_BD'

    # M_CC: signals that a poeration some king of operation was completed that took some time to complete, ??? response to C_CC??
    RESPONSE_M_CC = 'M_CC'
    # S_DI: signals that the command R_DI was accepted, it is followed by more data
    RESPONSE_S_DI = 'S_DI'
    # S_DR: ??? signals that the command R_DR was accepted, it is followed by more data
    RESPONSE_S_DR = 'S_DR'
    # S_FI: signals that the command R_FI was accepted, it is followed by more data
    RESPONSE_S_FI = 'S_FI'
    # S_FL: used to transfer blocks of file data to the control, signals that the command R_FL was accepted, it is followed by more data
    RESPONSE_S_FL = 'S_FL'

    # S_IN: found via bruteforce test, signals that the command R_IN was accepted, purpose unknown!
    # RESPONSE_S_IN = 'S_IN'

    # S_PR: ignals that the command R_PR and the parameter was accepted, it is followed by more data
    RESPONSE_S_PR = 'S_PR'
    # S_RI: signals that the command R_RI was accepted, it is followed by more data
    RESPONSE_S_RI = 'S_RI'

    # S_ST: found via bruteforce test, signals that the command R_ST was accepted, purpose unknown!
    # RESPONSE_S_ST = 'S_ST'

    # S_VR: signals that the command R_VR was accepted, it is followed by more data
    RESPONSE_S_VR = 'S_VR'

    COMMAND_R_VR_TYPE_CONTROL = 1
    COMMAND_R_VR_TYPE_NC_VERSION = 2
    COMMAND_R_VR_TYPE_PLC_VERSION = 3
    COMMAND_R_VR_TYPE_OPTIONS = 4
    COMMAND_R_VR_TYPE_ID = 5
    COMMAND_R_VR_TYPE_RELEASE_TYPE = 6
    COMMAND_R_VR_TYPE_SPLC_VERSION = 7

    # const for telegram C_CC / SetSysCmd
    SYSCMD_RESET_TNC = 1
    SYSCMD_STOP_TIMEUPDATE = 2
    SYSCMD_SET_BUF1024 = 3
    SYSCMD_SET_BUF512 = 4
    SYSCMD_SET_BUF2048 = 5
    SYSCMD_SET_BUF3072 = 6
    SYSCMD_SET_BUF4096 = 7
    SYSCMD_RESET_DNC = 8
    SYSCMD_RESET_LSV2 = 9  # not implemented
    SYSCMD_UPDATE_TNCOPT = 10
    SYSCMD_PUSH_PRESET_INTO_LOG = 11
    SYSCMD_SCREENDUMP = 12
    SYSCMD_ACTIVATE_PLCPGM = 13  # cmdpara: file name
    SYSCMD_OBSERVE_ADD_FILE = 15  # cmdpara: file name
    SYSCMD_OBSERVE_REMOVE_FILE = 16  # cmdpara: file name
    SYSCMD_OBSERVE_REMOVE_ALL = 17
    SYSCMD_ACTIVATE_MFSK = 18
    # C_FL: T_FD wird mit Antworttelegramm (T_OK/T_ER) quittiert
    SYSCMD_SECURE_FILE_SEND = 19
    SYSCMD_DELETE_TABLE_ENTRY = 20
    # tell control to generate operations log file, followed by filename and start time and date
    SYSCMD_GENERATE_OP_LOG = 27

    # const for relegram R_RI
    RUN_INFO_EXEC_STATE = 23
    RUN_INFO_SELECTED_PGM = 24
    RUN_INFO_PGM_STATE = 26

    # known program states
    PGM_STATE_STARTED = 0
    PGM_STATE_STOPPED = 1
    PGM_STATE_FINISHED = 2
    PGM_STATE_CANCELLED = 3
    PGM_STATE_INTERRUPTED = 4
    PGM_STATE_ERROR = 5
    PGM_STATE_ERROR_CLEARED = 6
    PGM_STATE_IDLE = 7
    PGM_STATE_UNDEFINED = 8

    # known execution states
    EXEC_STATE_MANUAL = 0
    EXEC_STATE_MDI = 1
    EXEC_STATE_PASS_REFERENCES = 2
    EXEC_STATE_SINGLE_STEP = 3
    EXEC_STATE_AUTOMATIC = 4
    EXEC_STATE_UNDEFINED = 5

    # known modes for command R_DR
    # mode switch for command R_DR to only read one entry at a time
    COMMAND_R_DR_MODE_SINGLE = 0x00
    # mode switch for command R_DR to only read multiple entries at a time, needs larger telegram size
    COMMAND_R_DR_MODE_MULTI = 0x01
    # mode switch for command R_DR to read drive information
    COMMAND_R_DR_MODE_DRIVES = 0x02

    C_FL_MODE_BINARY = 0x01  # is set by TNCcmd, seems to work for all filetypes
    R_FL_MODE_BINARY = 0x01 # enable binary file transfer, see also C_FL_MODE_BINARY

    def __init__(self, hostname, port=0, timeout=15.0, safe_mode=True):
        """init object variables and create socket"""
        logging.getLogger(__name__).addHandler(logging.NullHandler())

        self._llcom = LLLSV2Com(hostname, port, timeout)

        self._buffer_size = LLLSV2Com.DEFAULT_BUFFER_SIZE
        self._active_logins = list()

        if safe_mode:
            logging.info(
                'safe mode is active, login and system commands are restricted')
            self._known_logins = (LSV2.LOGIN_INSPECT, LSV2.LOGIN_FILETRANSFER)
            self._known_sys_cmd = (LSV2.SYSCMD_SET_BUF1024, LSV2.SYSCMD_SET_BUF512, LSV2.SYSCMD_SET_BUF2048, LSV2.SYSCMD_SET_BUF3072, LSV2.SYSCMD_SET_BUF4096,
                                   LSV2.SYSCMD_SECURE_FILE_SEND, LSV2.SYSCMD_GENERATE_OP_LOG)
        else:
            logging.info(
                'safe mode is off, login and system commands are not restricted. Use with caution!')
            self._known_logins = (LSV2.LOGIN_INSPECT, LSV2.LOGIN_DIAG, LSV2.LOGIN_PLCDEBUG, LSV2.LOGIN_FILETRANSFER, LSV2.LOGIN_MONITOR, LSV2.LOGIN_DSP,
                                  LSV2.LOGIN_DNC, LSV2.LOGIN_SCOPE, LSV2.LOGIN_STREAMAXES, LSV2.LOGIN_FILEPLC, LSV2.LOGIN_FILESYS)
            self._known_sys_cmd = (LSV2.SYSCMD_RESET_TNC, LSV2.SYSCMD_STOP_TIMEUPDATE, LSV2.SYSCMD_SET_BUF1024, LSV2.SYSCMD_SET_BUF512,
                                   LSV2.SYSCMD_SET_BUF2048, LSV2.SYSCMD_SET_BUF3072, LSV2.SYSCMD_SET_BUF4096, LSV2.SYSCMD_SECURE_FILE_SEND,
                                   LSV2.SYSCMD_RESET_DNC, LSV2.SYSCMD_RESET_LSV2, LSV2.SYSCMD_UPDATE_TNCOPT, LSV2.SYSCMD_PUSH_PRESET_INTO_LOG,
                                   LSV2.SYSCMD_SCREENDUMP, LSV2.SYSCMD_ACTIVATE_PLCPGM, LSV2.SYSCMD_OBSERVE_ADD_FILE, LSV2.SYSCMD_OBSERVE_REMOVE_FILE,
                                   LSV2.SYSCMD_OBSERVE_REMOVE_ALL, LSV2.SYSCMD_ACTIVATE_MFSK, LSV2.SYSCMD_SECURE_FILE_SEND, LSV2.SYSCMD_DELETE_TABLE_ENTRY)

        self._versions = None
        self._sys_par = None
        self._secure_file_send = False

    def connect(self):
        """connect to control"""
        self._llcom.connect()
        self._configure_connection()

    def disconnect(self):
        """logout of all open logins and close connection"""
        self.logout(login=None)
        self._llcom.disconnect()
        logging.debug('Connection to host closed')

    @staticmethod
    def _decode_error(content):
        """decode error codes to text"""
        byte_1, byte_2, = struct.unpack('!BB', content)
        error_text = get_error_text(byte_1, byte_2)
        logging.warning(
            'T_ER or T_BD received, an error occurred during the execution of the last command: %s', error_text)
        return error_text

    def _send_recive(self, command, expected_response, payload=None):
        """takes a command and payload, sends it to the control and checks
            if the response is as expected. Returns content if not an error"""
        if expected_response is None:
            self._llcom.telegram(command, payload, buffer_size=self._buffer_size, wait_for_response=False)
            logging.info(
                'command %s sent successfully, did not check for response', command)
            return True
        else:
            response, content = self._llcom.telegram(
                command, payload, buffer_size=self._buffer_size, wait_for_response=True)

            if response in expected_response:
                if content is not None and len(content) > 0:
                    logging.info(
                        'command %s executed successfully, received %s with %d bytes payload', command, response, len(content))
                    return content
                logging.info(
                    'command %s executed successfully, received %s without any payload', command, response)
                return True

            if response in LSV2.RESPONSE_T_ER:
                self._decode_error(content)
            else:
                logging.error(
                    'recived unexpected response %s to command %s. response code %s', response, command, content)

        return False

    def _send_recive_block(self, command, expected_response, payload=None):
        """takes a command and payload, sends it to the control and continues reading
            until the expected response is received."""
        response_buffer = list()
        response, content = self._llcom.telegram(
            command, payload, buffer_size=self._buffer_size)

        if response in LSV2.RESPONSE_T_ER:
            self._decode_error(content)
        elif response not in expected_response:
            logging.error(
                'recived unexpected response %s block read for command %s. response code %s', response, command, content)
            raise Exception('recived unexpected response {}'.format(response))
        else:
            while response in expected_response:
                response_buffer.append(content)
                response, content = self._llcom.telegram(
                    LSV2.RESPONSE_T_OK, buffer_size=self._buffer_size)
        return response_buffer

    def _send_recive_ack(self, command, payload=None):
        """sends command and pyload to control, returns True on T_OK"""
        response, content = self._llcom.telegram(
            command, payload, buffer_size=self._buffer_size)
        if response in LSV2.RESPONSE_T_OK:
            return True

        if response in LSV2.RESPONSE_T_ER:
            self._decode_error(content)
        else:
            logging.error(
                'recived unexpected response %s to command %s. response code %s', response, command, content)
        return False

    def _configure_connection(self):
        """This function sets up the communication parameters for file transfer. The buffer size is set based on the capabilitys of the control."""
        self.login(login=LSV2.LOGIN_INSPECT)
        control_type = self.get_versions()['Control']
        max_block_length = self.get_system_parameter()['Max_Block_Length']
        logging.info('setting connection settings for %s and block length %s',
                     control_type, max_block_length)

        if max_block_length >= 4096:
            if self.set_system_command(LSV2.SYSCMD_SET_BUF4096):
                self._buffer_size = 4096
            else:
                raise Exception('error in communication while setting buffer size to 4096')
        elif 3072 <= max_block_length < 4096:
            if self.set_system_command(LSV2.SYSCMD_SET_BUF3072):
                self._buffer_size = 3072
            else:
                raise Exception('error in communication while setting buffer size to 3072')
        elif 2048 <= max_block_length < 3072:
            if self.set_system_command(LSV2.SYSCMD_SET_BUF2048):
                self._buffer_size = 2048
            else:
                raise Exception('error in communication while setting buffer size to 2048')
        elif 1024 <= max_block_length < 2048:
            if self.set_system_command(LSV2.SYSCMD_SET_BUF1024):
                self._buffer_size = 1024
            else:
                raise Exception('error in communication while setting buffer size to 1024')
        elif 512 <= max_block_length < 1024:
            if self.set_system_command(LSV2.SYSCMD_SET_BUF512):
                self._buffer_size = 512
            else:
                raise Exception('error in communication while setting buffer size to 512')
        elif 256 <= max_block_length < 512:
            self._buffer_size = 256
        else:
            logging.error('could not decide on a buffer size for maximum message length of %d', max_block_length)
            raise Exception('unknown buffer size')

        if not self.set_system_command(LSV2.SYSCMD_SECURE_FILE_SEND):
            logging.warning('secure file transfer not supported? use fallback')
            self._secure_file_send = False
            #raise Exception('error in communication while enabling secure file send')
        else:
            self._secure_file_send = True

        self.login(login=LSV2.LOGIN_FILETRANSFER)
        logging.info(
            'successfully configured connection parameters and basic logins. selected buffer size is %d, use secure file send: %s', self._buffer_size, self._secure_file_send)

    def login(self, login, password=None):
        """some functions require certain access levels, to elevate this level a logon has to be performed. some levels require a password"""
        if login in self._active_logins:
            logging.debug('login already active')
            return True

        if login not in self._known_logins:
            logging.error('unknown or unsupported login')
            return False

        payload = bytearray()
        payload.extend(map(ord, login))
        payload.append(0x00)  # terminate string
        if password is not None:
            payload.extend(map(ord, password))
            payload.append(0x00)  # terminate string

        if not self._send_recive_ack(LSV2.COMMAND_A_LG, payload):
            logging.error('an error occurred during login for login %s', login)
            return False

        logging.info('login executed successfully for login %s', login)
        return True

    def logout(self, login=None):
        """drop access rights. if no user is supplied all active accrss rights are dropped."""
        if login in self._known_logins or login is None:
            logging.debug('logout for login %s', login)
            if login in self._active_logins or login is None:
                payload = bytearray()
                if login is not None:
                    payload.extend(map(ord, login))
                    payload.append(0x00)

                if self._send_recive_ack(LSV2.COMMAND_A_LO, payload):
                    logging.info(
                        'logout executed successfully for login %s', login)
                    return True
            else:
                logging.info(
                    'login %s was not active, logout not necessary', login)
                return True
        else:
            logging.warning('unknown or unsupported user')
        return False

    def set_system_command(self, command, parameter=None):
        """execute a system command on the control. command is one self._known_sys_cmd. If necessary additinal parameters can be supplied"""
        if command in self._known_sys_cmd:
            payload = bytearray()
            payload.extend(struct.pack('!H', command))
            if parameter is not None:
                payload.extend(map(ord, parameter))
                payload.append(0x00)  # terminate string
            if self._send_recive_ack(LSV2.COMMAND_C_CC, payload):
                return True
        logging.debug('unknown or unsupported system command')
        return False

    def get_system_parameter(self, force=False):
        """receive system parameters from the control and pares them to a dict."""
        if self._sys_par is not None and force is False:
            logging.debug(
                'version info already in memory, return previous values')
            return self._sys_par

        result = self._send_recive(
            command=LSV2.COMMAND_R_PR, expected_response=LSV2.RESPONSE_S_PR)
        if result:
            message_length = len(result)
            info_list = list()
            # as per comment in eclipse plugin, there might be a difference between a programming station and a real machine
            if message_length == 120:
                info_list = struct.unpack('!14L8B8L2BH4B2L2HL', result)
            elif message_length == 124:
                #raise NotImplementedError('this case for system parameters is unknown, please send log messages to add: {}'.format(result))
                logging.warning('messages with length 124 might not be decoded correctly!')
                info_list = struct.unpack('!14L8B8L2BH4B2L2HLL', result)
            else:
                raise ValueError('unexpected length {} of message content {}'.format(
                    message_length, result))
            sys_par = dict()
            sys_par['Marker_Start'] = info_list[0]
            sys_par['Markers'] = info_list[1]
            sys_par['Input_Start'] = info_list[2]
            sys_par['Inputs'] = info_list[3]
            sys_par['Output_Start'] = info_list[4]
            sys_par['Outputs'] = info_list[5]
            sys_par['Counter_Start'] = info_list[6]
            sys_par['Counters'] = info_list[7]
            sys_par['Timer_Start'] = info_list[8]
            sys_par['Timers'] = info_list[9]
            sys_par['Word_Start'] = info_list[10]
            sys_par['Words'] = info_list[11]
            sys_par['String_Start'] = info_list[12]
            sys_par['Strings'] = info_list[13]
            sys_par['String_Length'] = info_list[14]
            sys_par['Input_Word_Start'] = info_list[22]
            sys_par['Input Words'] = info_list[23]
            sys_par['Output_Word_Start'] = info_list[24]
            sys_par['Output_Words'] = info_list[25]
            sys_par['LSV2_Version'] = info_list[30]
            sys_par['LSV2_Version_Flags'] = info_list[31]
            sys_par['Max_Block_Length'] = info_list[32]
            sys_par['HDH_Bin_Version'] = info_list[33]
            sys_par['HDH_Bin_Revision'] = info_list[34]
            sys_par['ISO_Bin_Version'] = info_list[35]
            sys_par['ISO_Bin_Revision'] = info_list[36]
            sys_par['HardwareVersion'] = info_list[37]
            sys_par['LSV2_Version_Flags_Ex'] = info_list[38]
            sys_par['Max_Trace_Line'] = info_list[39]
            sys_par['Scope_Channels'] = info_list[40]
            sys_par['PW_Encryption_Key'] = info_list[41]
            logging.debug('got system parameters: %s', sys_par)
            self._sys_par = sys_par
            return self._sys_par
        logging.error('an error occurred while querying system parameters')
        return False

    def get_versions(self, force=False):
        """get version information from the control and return as dictionary"""
        if self._versions is not None and force is False:
            logging.debug(
                'version info already in memory, return previous values')
        else:
            info_data = dict()

            result = self._send_recive(LSV2.COMMAND_R_VR, LSV2.RESPONSE_S_VR, payload=struct.pack(
                '!B', LSV2.COMMAND_R_VR_TYPE_CONTROL))
            if result:
                info_data['Control'] = result.strip(b'\x00').decode('utf-8')
            else:
                raise Exception(
                    'Could not read version information from control')

            result = self._send_recive(LSV2.COMMAND_R_VR, LSV2.RESPONSE_S_VR, payload=struct.pack(
                '!B', LSV2.COMMAND_R_VR_TYPE_NC_VERSION))
            if result:
                info_data['NC_Version'] = result.strip(b'\x00').decode('utf-8')

            result = self._send_recive(LSV2.COMMAND_R_VR, LSV2.RESPONSE_S_VR, payload=struct.pack(
                '!B', LSV2.COMMAND_R_VR_TYPE_PLC_VERSION))
            if result:
                info_data['PLC_Version'] = result.strip(
                    b'\x00').decode('utf-8')

            result = self._send_recive(LSV2.COMMAND_R_VR, LSV2.RESPONSE_S_VR, payload=struct.pack(
                '!B', LSV2.COMMAND_R_VR_TYPE_OPTIONS))
            if result:
                info_data['Options'] = result.strip(b'\x00').decode('utf-8')

            result = self._send_recive(LSV2.COMMAND_R_VR, LSV2.RESPONSE_S_VR, payload=struct.pack(
                '!B', LSV2.COMMAND_R_VR_TYPE_ID))
            if result:
                info_data['ID'] = result.strip(b'\x00').decode('utf-8')

            result = self._send_recive(LSV2.COMMAND_R_VR, LSV2.RESPONSE_S_VR, payload=struct.pack(
                '!B', LSV2.COMMAND_R_VR_TYPE_RELEASE_TYPE))
            if result:
                info_data['Release_Type'] = result.strip(
                    b'\x00').decode('utf-8')

            result = self._send_recive(LSV2.COMMAND_R_VR, LSV2.RESPONSE_S_VR, payload=struct.pack(
                '!B', LSV2.COMMAND_R_VR_TYPE_SPLC_VERSION))
            if result:
                info_data['SPLC_Version'] = result.strip(
                    b'\x00').decode('utf-8')

            logging.debug('got version info: %s', info_data)
            self._versions = info_data

        return self._versions

    def get_program_status(self):
        """reads status of the currently active program.
           See https://github.com/tfischer73/Eclipse-Plugin-Heidenhain/issues/1"""
        self.login(login=LSV2.LOGIN_DNC)

        payload = bytearray()
        payload.extend(struct.pack('!H', self.RUN_INFO_PGM_STATE))

        result = self._send_recive(
            LSV2.COMMAND_R_RI, LSV2.RESPONSE_S_RI, payload)
        if result:
            pgm_state = struct.unpack('!H', result)[0]
            logging.debug('succesfully read state of active program: %s',
                          self.get_program_status_text(pgm_state))
            return pgm_state
        else:
            logging.error('an error occurred while querying program state')
        return False

    @staticmethod
    def get_program_status_text(code):
        """map status code to text"""
        return {LSV2.PGM_STATE_STARTED: 'Program started',
                LSV2.PGM_STATE_STOPPED: 'Program stopped',
                LSV2.PGM_STATE_FINISHED: 'Program finished',
                LSV2.PGM_STATE_CANCELLED: 'Program cancelled',
                LSV2.PGM_STATE_INTERRUPTED: 'Program interrupted by user',
                LSV2.PGM_STATE_ERROR: 'Program interrupted with error',
                LSV2.PGM_STATE_ERROR_CLEARED: 'Program interrupted with error, error was cleared',
                LSV2.PGM_STATE_IDLE: 'No Program running',
                LSV2.PGM_STATE_UNDEFINED: 'Program state undefined'}.get(code, 'Unknown Program state')

    def get_program_stack(self):
        """reads the path of the currently active programs and the line number of the execution.
           See https://github.com/tfischer73/Eclipse-Plugin-Heidenhain/issues/1"""
        self.login(login=LSV2.LOGIN_DNC)

        payload = bytearray()
        payload.extend(struct.pack('!H', self.RUN_INFO_SELECTED_PGM))

        result = self._send_recive(
            LSV2.COMMAND_R_RI, LSV2.RESPONSE_S_RI, payload=payload)
        if result:
            stack_info = dict()
            stack_info['Line'] = struct.unpack('!L', result[:4])[0]
            stack_info['Main_PGM'] = result[4:].split(b'\x00')[0].decode().strip('\x00').replace('\\', '/')
            stack_info['Current_PGM'] = result[4:].split(b'\x00')[1].decode().strip('\x00').replace('\\', '/')
            logging.debug(
                'succesfully read active program stack and line number: %s', stack_info)
            return stack_info
        else:
            logging.error(
                'an error occurred while querying active program state')
        return False

    def get_execution_status(self):
        """reads the execution status.
           See https://github.com/drunsinn/pyLSV2/issues/1"""
        self.login(login=LSV2.LOGIN_DNC)

        payload = bytearray()
        payload.extend(struct.pack('!H', self.RUN_INFO_EXEC_STATE))

        result = self._send_recive(
            LSV2.COMMAND_R_RI, LSV2.RESPONSE_S_RI, payload)
        if result:
            exec_state = struct.unpack('!H', result)[0]
            return exec_state
        else:
            logging.error('an error occurred while querying execution state')
        return False

    @staticmethod
    def get_execution_status_text(code):
        """map status code to text
           See https://github.com/drunsinn/pyLSV2/issues/1"""
        return {LSV2.EXEC_STATE_MANUAL: 'Manual execution',
                LSV2.EXEC_STATE_MDI: 'MDI execution',
                LSV2.EXEC_STATE_PASS_REFERENCES: 'Pass References execution',
                LSV2.EXEC_STATE_SINGLE_STEP: 'Single Step execution',
                LSV2.EXEC_STATE_AUTOMATIC: 'Automatic execution',
                LSV2.EXEC_STATE_UNDEFINED: 'Execution state undefined'}.get(code, 'Unknown Execution state')

    def get_directory_info(self, remote_directory=None):
        """get information on the current working directory"""
        if remote_directory is not None and not self.change_directory(remote_directory):
            logging.error(
                'could not change current directory to read directory info for %s', remote_directory)

        result = self._send_recive(LSV2.COMMAND_R_DI, LSV2.RESPONSE_S_DI)
        if result:
            dir_info = dict()
            dir_info['Free Size'] = struct.unpack('!L', result[:4])

            attribute_list = list()
            for i in range(4, len(result[4:128]), 4):
                attr = result[i:i + 4].decode().strip('\x00')
                if len(attr) > 0:
                    attribute_list.append(attr)

            dir_info['Dir_Attributs'] = attribute_list
            dir_info['unknown'] = result[128:164]
            dir_info['Path'] = result[164:].decode().strip(
                '\x00').replace('\\', '/')
            logging.debug(
                'succesfully received directory information %s', dir_info)

            return dir_info
        else:
            logging.error('an error occurred while querying directory info')
        return False

    def change_directory(self, remote_directory):
        """change the current working directoyon the control"""
        dir_path = remote_directory.replace('\\', '/')
        payload = bytearray()
        payload.extend(map(ord, dir_path))
        payload.append(0x00)
        if self._send_recive_ack(LSV2.COMMAND_C_DC, payload=payload):
            logging.debug('changed working directory to %s', dir_path)
            return True
        else:
            logging.error('an error occurred while changing directory')
        return False

    def get_file_info(self, remote_file_path):
        """get information about the file or folder? and return the information as a dict"""
        file_path = remote_file_path.replace('\\', '/')
        payload = bytearray()
        payload.extend(map(ord, file_path))
        payload.append(0x00)

        result = self._send_recive(
            LSV2.COMMAND_R_FI, LSV2.RESPONSE_S_FI, payload=payload)
        if result:
            file_info = dict()
            file_info['Size'] = struct.unpack('!L', result[:4])[0]
            file_info['Timestamp'] = datetime.datetime.fromtimestamp(
                struct.unpack('!L', result[4:8])[0])
            file_info['Name'] = result[12:].decode().strip(
                '\x00').replace('\\', '/')
            file_info['Attributs'] = struct.unpack('!L', result[8:12])[0]
            logging.debug(
                'succesfully received file information %s', file_info)
            return file_info
        else:
            logging.warning(
                'an error occurred while querying file info this might also indicate that it does not exist %s', remote_file_path)
        return False

    def get_directory_content(self):
        """get content of current working directory"""
        dir_content = list()
        payload = bytearray()
        payload.append(self.COMMAND_R_DR_MODE_SINGLE)

        result = self._send_recive_block(
            LSV2.COMMAND_R_DR, LSV2.RESPONSE_S_DR, payload)
        logging.debug(
            'received %d entries for directory content information', len(result))
        for entry in result:
            file_info = dict()
            file_info['Size'] = struct.unpack('!L', entry[:4])[0]
            file_info['Timestamp'] = datetime.datetime.fromtimestamp(
                struct.unpack('!L', entry[4:8])[0])
            file_info['Name'] = entry[12:].decode().strip(
                '\x00').replace('\\', '/')
            file_info['Attributs'] = struct.unpack('!L', entry[8:12])[0]
            dir_content.append(file_info)
        logging.debug(
            'succesfully received directory information %s', dir_content)
        return dir_content

    def get_drive_info(self):
        """get content of current working directory"""
        drives_list = list()
        payload = bytearray()
        payload.append(self.COMMAND_R_DR_MODE_DRIVES)

        result = self._send_recive_block(
            LSV2.COMMAND_R_DR, LSV2.RESPONSE_S_DR, payload)
        logging.debug(
            'received %d packet of for drive information', len(result))
        for entry in result:
            info_list = entry.split(b':\x00')
            for drive in info_list[:-1]:
                drive_info = dict()
                drive_name = drive[12:].decode().strip('\x00')
                drive_info['Name'] = drive_name + ':/'
                drive_info['unknown'] = drive
                drives_list.append(drive_info)

        logging.debug('succesfully received drive information %s', drives_list)
        return drives_list

    def make_directory(self, dir_path):
        """create directory on control. split path into separate parts and iterate over every segment.
        starting from the base check each segment and create the directory if necessary"""
        path_parts = dir_path.replace(
            '\\', '/').split('/')  # convert path to unix style
        path_to_check = ''
        for part in path_parts:
            path_to_check += part + '/'
            # no file info -> does not exist and has to be created
            if self.get_file_info(path_to_check) is False:
                payload = bytearray()
                payload.extend(map(ord, path_to_check))
                payload.append(0x00)  # terminate string
                if self._send_recive_ack(command=LSV2.COMMAND_C_DM, payload=payload):
                    logging.debug('Directory created succesfully')
                else:
                    raise Exception(
                        'an error occurred while creating directory {}'.format(dir_path))
            else:
                logging.debug('nothing to do as this segment already exists')
        return True

    def delete_empty_directory(self, dir_path):
        """deleta a directory on the control, only works if it is empty"""
        dir_path = dir_path.replace('\\', '/')
        payload = bytearray()
        payload.extend(map(ord, dir_path))
        payload.append(0x00)
        if not self._send_recive_ack(command=LSV2.COMMAND_C_DD, payload=payload):
            logging.warning(
                'an error occurred while deleting directory %s, this might also indicate that it it does not exist', dir_path)
            return False
        logging.debug('succesfully deleted folder %s', dir_path)
        return True

    def delete_file(self, file_path):
        """delete a file on control"""
        file_path = file_path.replace('\\', '/')
        payload = bytearray()
        payload.extend(map(ord, file_path))
        payload.append(0x00)
        if not self._send_recive_ack(command=LSV2.COMMAND_C_FD, payload=payload):
            logging.warning(
                'an error occurred while deleting file %s, this might also indicate that it it does not exist', file_path)
            return False
        logging.debug('succesfully deleted file %s', file_path)
        return True

    def copy_local_file(self, source_path, target_path):
        """copy a file on control"""
        source_path = source_path.replace('\\', '/')
        target_path = target_path.replace('\\', '/')

        if '/' in source_path:
            # change directory
            source_file_name = source_path.split('/')[-1]
            source_folder = source_path.rstrip(source_file_name)
            if not self.change_directory(remote_directory=source_folder):
                raise Exception('could not open the source directoy')
        else:
            source_file_name = source_path
            source_folder = '.'

        if target_path.endswith('/'):
            target_path += source_file_name

        payload = bytearray()
        payload.extend(map(ord, source_file_name))
        payload.append(0x00)
        payload.extend(map(ord, target_path))
        payload.append(0x00)
        logging.debug('prepare to copy file %s from %s to %s',
                      source_file_name, source_folder, target_path)
        if not self._send_recive_ack(command=LSV2.COMMAND_C_FC, payload=payload):
            logging.warning(
                'an error occurred copying file %s to %s', source_path, target_path)
            return False
        logging.debug('succesfully copied file %s', source_path)
        return True

    def move_local_file(self, source_path, target_path):
        """move a file on control"""
        source_path = source_path.replace('\\', '/')
        target_path = target_path.replace('\\', '/')

        if '/' in source_path:
            source_file_name = source_path.split('/')[-1]
            source_folder = source_path.rstrip(source_file_name)
            if not self.change_directory(remote_directory=source_folder):
                raise Exception('could not open the source directoy')
        else:
            source_file_name = source_path
            source_folder = '.'

        if target_path.endswith('/'):
            target_path += source_file_name

        payload = bytearray()
        payload.extend(map(ord, source_file_name))
        payload.append(0x00)
        payload.extend(map(ord, target_path))
        payload.append(0x00)
        logging.debug('prepare to move file %s from %s to %s',
                      source_file_name, source_folder, target_path)
        if not self._send_recive_ack(command=LSV2.COMMAND_C_FR, payload=payload):
            logging.warning(
                'an error occurred moving file %s to %s', source_path, target_path)
            return False
        logging.debug('succesfully moved file %s', source_path)
        return True

    def send_file(self, local_path, remote_path, override_file=False, binary_mode=False):
        """send file to the control, parameter override_file allowes replacing an existing file
            with parameter binary mode you can select the transfer mode. it it is not set the filename is
            checked against a know list of binary extentions"""
        local_file = Path(local_path)

        if not local_file.is_file():
            logging.error(
                'the supplied path %s did not resolve to a file', local_file)
            raise Exception('local file does not exist! {}'.format(local_file))

        remote_path = remote_path.replace('\\', '/')

        if '/' in remote_path:
            if remote_path.endswith('/'):  # no filename given
                remote_file_name = local_file.name
                remote_folder = remote_path
            else:
                remote_file_name = remote_path.split('/')[-1]
                remote_folder = remote_path.rstrip(remote_file_name)
                if not self.change_directory(remote_directory=remote_folder):
                    raise Exception(
                        'could not open the source directory {}'.format(remote_folder))
        else:
            remote_file_name = remote_path
            remote_folder = self.get_directory_info()['Path']  # get pwd
        remote_folder = remote_folder.rstrip('/')

        if not self.get_directory_info(remote_folder):
            logging.debug('remote path does not exist, create folder(s)')
            self.make_directory(remote_folder)

        remote_info = self.get_file_info(
            remote_folder + '/' + remote_file_name)

        if remote_info:
            logging.debug('remote path exists and points to files')
            if override_file:
                if not self.delete_file(remote_folder + '/' + remote_file_name):
                    raise Exception('something went wrong while deleting file {}'.format(
                        remote_folder + '/' + remote_file_name))
            else:
                logging.warning(
                    'remote file already exists, override was not set')
                return False

        logging.debug('ready to send file from %s to %s',
                      local_file, remote_folder + '/' + remote_file_name)

        payload = bytearray()
        payload.extend(map(ord, remote_folder + '/' + remote_file_name))
        payload.append(0x00)
        if binary_mode or self._is_file_type_binary(local_path):
            payload.append(LSV2.C_FL_MODE_BINARY)
            logging.info('selecting binary transfer mode for this file type')
        response, content = self._llcom.telegram(
            LSV2.COMMAND_C_FL, payload, buffer_size=self._buffer_size)

        if response in self.RESPONSE_T_OK:
            with local_file.open('rb') as input_buffer:
                while True:
                    # use current buffer size but reduce by 10 to make sure it fits together with command and size
                    buffer = input_buffer.read(self._buffer_size - 10)
                    if not buffer:
                        # finished reading file
                        break

                    response, content = self._llcom.telegram(
                        LSV2.RESPONSE_S_FL, buffer, buffer_size=self._buffer_size)
                    if response in self.RESPONSE_T_OK:
                        pass
                    else:
                        if response in self.RESPONSE_T_ER:
                            self._decode_error(content)
                        else:
                            logging.error(
                                'could not send data with error %s', response)
                        return False

            # signal that no more data is being sent
            if self._secure_file_send:
                if not self._send_recive(command=LSV2.RESPONSE_T_FD, expected_response=LSV2.RESPONSE_T_OK, payload=None):
                    logging.error('could not send end of file with error')
                    return False
            else:
                if not self._send_recive(command=LSV2.RESPONSE_T_FD, expected_response=None, payload=None):
                    logging.error('could not send end of file with error')
                    return False

        else:
            if response in self.RESPONSE_T_ER:
                self._decode_error(content)
            else:
                logging.error('could not send file with error %s', response)
            return False

        return True

    def recive_file(self, remote_path, local_path, override_file=False, binary_mode=False):
        '''send file to the control, parameter override_file allowes replacing an existing file
            with parameter binary mode you can select the transfer mode. it it is not set the filename is
            checked against a know list of binary extentions'''

        remote_file_info = self.get_file_info(remote_path)
        if not remote_file_info:
            logging.error('remote file does not exist: %s', remote_path)
            return False

        local_file = Path(local_path)
        if local_file.is_dir():
            local_file.joinpath(remote_path.split('/')[-1])

        if local_file.is_file():
            logging.debug('local path exists and points to file')
            if override_file:
                local_file.unlink()
            else:
                logging.warning(
                    'remote file already exists, override was not set')
                return False

        logging.debug('loading file from %s to %s', remote_path, local_file)

        payload = bytearray()
        payload.extend(map(ord, remote_path))
        payload.append(0x00)
        if binary_mode or self._is_file_type_binary(remote_path):
            payload.append(LSV2.R_FL_MODE_BINARY)  # force binary transfer
            logging.info('useing binary transfer mode')
        response, content = self._llcom.telegram(
            LSV2.COMMAND_R_FL, payload, buffer_size=self._buffer_size)

        with local_file.open('wb') as out_file:
            #file_buffer = bytearray()
            if response in self.RESPONSE_S_FL:
                # file_buffer.extend(content)
                if binary_mode:
                    out_file.write(content)
                else:
                    out_file.write(content.replace(b'\x00', b'\r\n'))
                logging.debug(
                    'received first block of file file %s', remote_path)

                while True:
                    response, content = self._llcom.telegram(
                        LSV2.RESPONSE_T_OK, payload=None, buffer_size=self._buffer_size)
                    if response in self.RESPONSE_S_FL:
                        # file_buffer.extend(content)
                        if binary_mode:
                            out_file.write(content)
                        else:
                            out_file.write(content.replace(b'\x00', b''))
                        logging.debug(
                            'received %d more bytes for file', len(content))
                    elif response in self.RESPONSE_T_FD:
                        logging.info('finished loading file')
                        break
                    else:
                        if response in self.RESPONSE_T_ER or response in self.RESPONSE_T_BD:
                            logging.error(
                                'an error occurred while loading the first block of data for file %s : %s', remote_path, self._decode_error(content))
                        else:
                            logging.error(
                                'something went wrong while receiving file data %s', remote_path)
                        return False
            else:
                if response in self.RESPONSE_T_ER or response in self.RESPONSE_T_BD:
                    logging.error('an error occurred while loading the first block of data for file %s : %s',
                                  remote_path, self._decode_error(content))
                else:
                    logging.error(
                        'could not load file with error %s', response)
                return False

        logging.info('received %d bytes transfer complete for file %s to %s',
                     local_file.stat().st_size, remote_path, local_file)

        return True

    def _is_file_type_binary(self, file_name):
        for bin_type in self.BIN_FILES:
            if file_name.endswith(bin_type):
                return True
        return False

    def _test_command(self, command_string, payload=None):
        """check commands for validity"""
        response, content = self._llcom.telegram(
            command_string, payload, buffer_size=self._buffer_size)
        if content is None:
            response_length = -1
        else:
            response_length = len(content)
        if response in LSV2.RESPONSE_T_ER:
            if len(content) == 2:
                byte_1, byte_2, = struct.unpack('!BB', content)
                error_text = get_error_text(byte_1, byte_2)
            else:
                error_text = 'Unknown Error Number {}'.format(content)
        else:
            error_text = 'NONE'
        return 'sent {} payload {} received {} message_length {} content {} error text : {}'.format(command_string, payload, response, response_length, content, error_text)
