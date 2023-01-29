#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Constant values used in LSV2"""
from enum import Enum, IntEnum

#: enable/disable binary file transfer for C_FL and R_FL
MODE_BINARY = 0x01
MODE_NON_BIN = 0x00

PATH_SEP = "\\"

#: Regex pattern for Klartext file names
REGEX_FILE_NAME_H = r"[\$A-Za-z0-9_-]*\.[hH]$"

#: Regex pattern for DIN/ISO file names
REGEX_FILE_NAME_I = r"[\$A-Za-z0-9_-]*\.[iI]$"

#: List of file types which should be transferred in binary mode
BIN_FILES = (
    ".ads",
    ".bak",
    ".bck",
    ".bin",
    ".bmp",
    ".bmx",
    ".chm",
    ".cyc",
    ".cy%",
    ".dmp",
    ".dll",
    ".eak",
    ".elf",
    ".enc",
    ".exe",
    ".gds",
    ".gif",
    ".hbi",
    ".he",
    ".ioc",
    ".iocp",
    ".jpg",
    ".jpeg",
    ".map",
    ".mds",
    ".mo",
    ".omf",
    ".pdf",
    ".png",
    ".pyc",
    ".s",
    ".sds",
    ".sk",
    ".str",
    ".xml",
    ".xls",
    ".xrs",
    ".zip",
)


class DriveName(str, Enum):
    """Enum for drive names found on TNC controls"""

    TNC = "TNC:"
    """partition TNC, contains NC programs and tables"""

    PLC = "PLC:"
    """partition PLC, contains PLC program and configuration data"""

    LOG = "LOG:"
    """partition LOG, contains log files. Not available on all controls"""

    SYS = "SYS:"
    """partition SYS, ???"""


class ControlType(Enum):
    """Enum for generation and type of control"""

    MILL_NEW = 1
    """new style interface for milling controls: TNC128, TNC320, TNC620 and TNC640"""

    MILL_OLD = 2
    """old style interface for milling controls: iTNC530"""

    LATHE_NEW = 3
    """new stype interface for lathe controls: CNCpilot640"""

    LATHE_OLD = 4
    """old stype interface for lathe controls: ?"""

    UNKNOWN = -1
    """unknown control type"""


class Login(str, Enum):
    """Enum for the different login roles"""

    INSPECT = "INSPECT"
    """enables read only functions"""

    DIAG = "DIAGNOSTICS"
    """enables logbook / recover"""

    PLCDEBUG = "PLCDEBUG"
    """enables write access to PLC, requires password"""

    FILETRANSFER = "FILE"
    """enables filesystem access to tnc drive"""

    MONITOR = "MONITOR"
    """enables TNC remote access and screen dump"""

    DSP = "DSP"
    """enables DSP functions"""

    DNC = "DNC"
    """enables DNC functions"""

    SCOPE = "OSZI"
    """enables Remote Scope, requires password"""

    STREAMAXES = "STREAMAXES"
    """enables Streaming of axis data, requires password"""

    FILEPLC = "FILEPLC"
    """enables file system access to plc drive, requires password"""

    FILESYS = "FILESYS"
    """enables file system access to sys drive, requires password"""

    FILELOG = "FILELOG"
    """enables file system access to log drive, requires password"""

    DATA = "DATA"
    """??? used for R_DP ???"""


class ExecState(IntEnum):
    """Enum for execution states"""

    MANUAL = 0
    """Manual mode"""

    MDI = 1
    """MDI/manual data input mode"""

    PASS_REFERENCES = 2
    """pass axis ref mode"""

    SINGLE_STEP = 3
    """program execution in single step mode"""

    AUTOMATIC = 4
    """program execution in automatic mode"""

    UNDEFINED = 5
    """execution mode undefined"""


class PgmState(IntEnum):
    """Enum for state of selected program"""

    STARTED = 0
    STOPPED = 1
    FINISHED = 2
    CANCELLED = 3
    INTERRUPTED = 4
    ERROR = 5
    ERROR_CLEARED = 6
    IDLE = 7
    UNDEFINED = 8


class MemoryType(IntEnum):
    """Enum of memory types for reading from PLC memory"""

    MARKER = 1
    INPUT = 2
    OUTPUT = 3
    COUNTER = 4
    TIMER = 5
    BYTE = 6
    WORD = 7
    DWORD = 8
    STRING = 9
    INPUT_WORD = 10
    OUTPUT_WORD = 11


class LSV2StatusCode(IntEnum):
    """Enum for LSV2 protocol error numbers
    range 0 - 19: protocol or transmission errors
    range 20 - 99: telegram errors
    range 100 - 200: block transfer errors
    """

    LSV2_OK = 0

    # receiving
    LSV2_TIMEOUT = 1
    LSV2_NO_ENQ = 2
    LSV2_TIMEOUT2 = 3
    LSV2_WRONG_CHAR = 4
    LSV2_TO_LONG = 5
    LSV2_WRONG_BBC = 6
    LSV2_NO_EOT = 7
    LSV2_TIMEOUT3 = 12
    LSV2_NO_MESSAGE = 16

    # sending
    LSV2_AP_ERROR = 8
    LSV2_AP_COL = 9
    LSV2_NO_QUITT = 10
    LSV2_TX_ERROR = 11

    # interface
    LSV2_Q_MSG = 0
    LSV2_Q_EMPTY = 1
    LSV2_COM_CLOSED = 13

    # init
    LSV2_NO_OPEN = 14
    LSV2_WRONG_PARAMS = 15

    # misc
    LSV2_NO_ACK = 17
    LSV2_MSG_OK = 19

    # telegram errors
    T_ER_BAD_FORMAT = 20
    T_ER_UNEXPECTED_TELE = 21
    T_ER_UNKNOWN_TELE = 22
    T_ER_NO_PRIV = 23
    T_ER_WRONG_PARA = 24
    T_ER_BREAK = 25
    T_ER_BAD_KEY = 30
    T_ER_BAD_FNAME = 31
    T_ER_NO_FILE = 32
    T_ER_OPEN_FILE = 33
    T_ER_FILE_EXISTS = 34
    T_ER_BAD_FILE = 35
    T_ER_NO_DELETE = 36
    T_ER_NO_NEW_FILE = 37
    T_ER_NO_CHANGE_ATT = 38
    T_ER_BAD_EMULATEKEY = 39
    T_ER_NO_MP = 40
    T_ER_NO_WIN = 41
    T_ER_WIN_NOT_AKTIV = 42
    T_ER_ANZ = 43
    T_ER_FONT_NOT_DEFINED = 44
    T_ER_FILE_ACCESS = 45
    T_ER_WRONG_DNC_STATUS = 46
    T_ER_CHANGE_PATH = 47
    T_ER_NO_RENAME = 48
    T_ER_NO_LOGIN = 49
    T_ER_BAD_PARAMETER = 50
    T_ER_BAD_NUMBER_FORMAT = 51
    T_ER_BAD_MEMADR = 52
    T_ER_NO_FREE_SPACE = 53
    T_ER_DEL_DIR = 54
    T_ER_NO_DIR = 55
    T_ER_OPERATING_MODE = 56
    T_ER_NO_NEXT_ERROR = 57
    T_ER_ACCESS_TIMEOUT = 58
    T_ER_NO_WRITE_ACCESS = 59
    T_ER_STIB = 60
    T_ER_REF_NECESSARY = 61
    T_ER_PLC_BUF_FULL = 62
    T_ER_NOT_FOUND = 63
    T_ER_WRONG_FILE = 64
    T_ER_NO_MATCH = 65
    T_ER_TOO_MANY_TPTS = 66
    T_ER_NOT_ACTIVATED = 67
    T_ER_DSP_CHANNEL = 70
    T_ER_DSP_PARA = 71
    T_ER_OUT_OF_RANGE = 72
    T_ER_INVALID_AXIS = 73
    T_ER_STREAMING_ACTIVE = 74
    T_ER_NO_STREAMING_ACTIVE = 75
    T_ER_TO_MANY_OPEN_TCP = 80
    T_ER_NO_FREE_HANDLE = 81
    T_ER_PLCMEMREMA_CLEAR = 82
    T_ER_OSZI_CHSEL = 83
    LSV2_BUSY = 90
    LSV2_X_BUSY = 91
    LSV2_NOCONNECT = 92
    LSV2_BAD_BACKUP_FILE = 93
    LSV2_RESTORE_NOT_FOUND = 94
    LSV2_DLL_NOT_INSTALLED = 95
    LSV2_BAD_CONVERT_DLL = 96
    LSV2_BAD_BACKUP_LIST = 97
    LSV2_UNKNOWN_ERROR = 99

    # block transfer errors
    T_BD_NO_NEW_FILE = 100
    T_BD_NO_FREE_SPACE = 101
    T_BD_FILE_NOT_ALLOWED = 102
    T_BD_BAD_FORMAT = 103
    T_BD_BAD_BLOCK = 104
    T_BD_END_PGM = 105
    T_BD_ANZ = 106
    T_BD_WIN_NOT_DEFINED = 107
    T_BD_WIN_CHANGED = 108
    T_BD_DNC_WAIT = 110
    T_BD_CANCELLED = 111
    T_BD_OSZI_OVERRUN = 112
    T_BD_FD = 200

    # plain error message (TODO see global var usererrortext)
    T_USER_ERROR = 255

    T_ER_NON = -1
    """not an valid error code. devault value if no error occurred"""


class KeyCode(IntEnum):
    """Keycodes"""

    #: key codes
    LOWER_A = 0x0061
    LOWER_B = 0x0062
    LOWER_C = 0x0063
    LOWER_D = 0x0064
    LOWER_E = 0x0065
    LOWER_F = 0x0066
    LOWER_G = 0x0067
    LOWER_H = 0x0068
    LOWER_I = 0x0069
    LOWER_J = 0x006A
    LOWER_K = 0x006B
    LOWER_L = 0x006C
    LOWER_M = 0x006D
    LOWER_N = 0x006E
    LOWER_O = 0x006F
    LOWER_P = 0x0070
    LOWER_Q = 0x0071
    LOWER_R = 0x0072
    LOWER_S = 0x0073
    LOWER_T = 0x0074
    LOWER_U = 0x0075
    LOWER_V = 0x0076
    LOWER_W = 0x0077
    LOWER_X = 0x0078
    LOWER_Y = 0x0079
    LOWER_Z = 0x007A

    UPPER_A = 0x0041
    UPPER_B = 0x0042
    UPPER_C = 0x0043
    UPPER_D = 0x0044
    UPPER_E = 0x0045
    UPPER_F = 0x0046
    UPPER_G = 0x0047
    UPPER_H = 0x0048
    UPPER_I = 0x0049
    UPPER_J = 0x004A
    UPPER_K = 0x004B
    UPPER_L = 0x004C
    UPPER_M = 0x004D
    UPPER_N = 0x004E
    UPPER_O = 0x004F
    UPPER_P = 0x0050
    UPPER_Q = 0x0051
    UPPER_R = 0x0052
    UPPER_S = 0x0053
    UPPER_T = 0x0054
    UPPER_U = 0x0055
    UPPER_V = 0x0056
    UPPER_W = 0x0057
    UPPER_X = 0x0058
    UPPER_Y = 0x0059
    UPPER_Z = 0x005A

    NUMBER_0 = 0x0030
    NUMBER_1 = 0x0031
    NUMBER_2 = 0x0032
    NUMBER_3 = 0x0033
    NUMBER_4 = 0x0034
    NUMBER_5 = 0x0035
    NUMBER_6 = 0x0036
    NUMBER_7 = 0x0037
    NUMBER_8 = 0x0038
    NUMBER_9 = 0x0039

    BOTTOM_SK0 = 0x0180
    BOTTOM_SK1 = 0x0181
    BOTTOM_SK2 = 0x0182
    BOTTOM_SK3 = 0x0183
    BOTTOM_SK4 = 0x0184
    BOTTOM_SK5 = 0x0185
    BOTTOM_SK6 = 0x0186
    BOTTOM_SK7 = 0x0187
    BOTTOM_SK8 = 0x0188
    BOTTOM_SK9 = 0x0189

    RIGHT_SK0 = 0x0160
    RIGHT_SK1 = 0x0161
    RIGHT_SK2 = 0x0162
    RIGHT_SK3 = 0x0163
    RIGHT_SK4 = 0x0164
    RIGHT_SK5 = 0x0165
    RIGHT_SK6 = 0x0166
    RIGHT_SK7 = 0x0167
    RIGHT_SK8 = 0x0168

    LEFT_SK0 = 0x0150
    LEFT_SK1 = 0x0151
    LEFT_SK2 = 0x0152
    LEFT_SK3 = 0x0153
    LEFT_SK4 = 0x0154
    LEFT_SK5 = 0x0155
    LEFT_SK6 = 0x0156
    LEFT_SK7 = 0x0157
    LEFT_SK8 = 0x0158
    LEFT_SK9 = 0x0159

    BACKSPACE = 0x0008
    LINE_FEED = 0x000A
    CARIDGE_RETURN = 0x000D
    SPACE = 0x020
    COLON = 0x03A

    SK_NEXT = 0x019D
    SK_PREVIOUS = 0x019E
    ARROW_UP = 0x01A0
    ARROW_DOWN = 0x01A1
    ARROW_LEFT = 0x01A2
    ARROW_RIGHT = 0x01A3

    ENT = 0x01A8
    NOENT = 0x01A9
    DEL = 0x01AB
    END = 0x01AC
    GOTO = 0x01AD
    CE = 0x01AE

    AXIS_X = 0x01B0
    AXIS_Y = 0x01B1
    AXIS_Z = 0x01B2
    ANGULAR_AXIS_1 = 0x01B3
    ANGULAR_AXIS_2 = 0x01B4
    TOGGEL_POLAR = 0x01B8
    TOGGEL_INC = 0x01B9
    PROG_Q = 0x01BA
    ACTPOS = 0x01BB
    TOGGEL_SIGN = 0x01BC
    DECIMAL_POINT = 0x01BD
    PROG_PGM_CALL = 0x01D0
    PROG_TOOL_DEF = 0x01D1
    PROG_TOOL_CALL = 0x01D2
    PROG_CYC_DEF = 0x01D3
    PROG_CYC_CALL = 0x01D4
    # PROG_CYC_CAL = PROG_CYC_CALL
    PROG_LBL = 0x01D5
    PROG_LBL_CALL = 0x01D6
    PROG_L = 0x01D7
    PROG_C = 0x01D8
    PROG_CR = 0x01D9
    PROG_CT = 0x01DA
    PROG_CC = 0x01DB
    PROG_RND = 0x01DC
    PROG_CHF = 0x01DD
    PROG_FK = 0x01DE
    PROG_TOUCH_PROBE = 0x01DF
    PROG_STOP = 0x01E0
    PROG_APPR_DEP = 0x01E1

    MODE_MANUAL = 0x01C0
    MODE_SINGLE_STEP = 0x01C2
    MODE_AUTOMATIC = 0x01C3
    MODE_PGM_EDIT = 0x01C4
    MODE_HANDWHEEL = 0x01C5
    MODE_PGM_SIMULATION = 0x01C6
    MOD_DIALOG = 0x01C7
    PGMMGT = 0x01CB

    TI = 0x01C1
    HELP = 0x01ED
    INFO = 0x01EE
    CALC = 0x01EF


class OldKeyCode(IntEnum):
    """Keycodes from old LSV2 docu"""

    # ASCII keys: low byte = 0x50, high byte = ascii code
    LOWER_A = 0x6150
    LOWER_B = 0x6250
    LOWER_C = 0x6350
    LOWER_D = 0x6450
    LOWER_E = 0x6550
    LOWER_F = 0x6650
    LOWER_G = 0x6750
    LOWER_H = 0x6850
    LOWER_I = 0x6950
    LOWER_J = 0x6A50
    LOWER_K = 0x6B50
    LOWER_L = 0x6C50
    LOWER_M = 0x6D50
    LOWER_N = 0x6E50
    LOWER_O = 0x6F50
    LOWER_P = 0x7050
    LOWER_Q = 0x7150
    LOWER_R = 0x7250
    LOWER_S = 0x7350
    LOWER_T = 0x7450
    LOWER_U = 0x7550
    LOWER_V = 0x7650
    LOWER_W = 0x7750
    LOWER_X = 0x7850
    LOWER_Y = 0x7950
    LOWER_Z = 0x7A50

    UPPER_A = 0x4150
    UPPER_B = 0x4250
    UPPER_C = 0x4350
    UPPER_D = 0x4450
    UPPER_E = 0x4550
    UPPER_F = 0x4650
    UPPER_G = 0x4750
    UPPER_H = 0x4850
    UPPER_I = 0x4950
    UPPER_J = 0x4A50
    UPPER_K = 0x4B50
    UPPER_L = 0x4C50
    UPPER_M = 0x4D50
    UPPER_N = 0x4E50
    UPPER_O = 0x4F50
    UPPER_P = 0x5050
    UPPER_Q = 0x5150
    UPPER_R = 0x5250
    UPPER_S = 0x5350
    UPPER_T = 0x5450
    UPPER_U = 0x5550
    UPPER_V = 0x5650
    UPPER_W = 0x5750
    UPPER_X = 0x5850
    UPPER_Y = 0x5950
    UPPER_Z = 0x5A50

    NUMBER_0 = 0x3050
    NUMBER_1 = 0x3150
    NUMBER_2 = 0x3250
    NUMBER_3 = 0x3350
    NUMBER_4 = 0x3450
    NUMBER_5 = 0x3550
    NUMBER_6 = 0x3650
    NUMBER_7 = 0x3750
    NUMBER_8 = 0x3850
    NUMBER_9 = 0x3950

    TOGGEL_SIGN = 0x007C
    END = 0x0077
    NOENT = 0x005F
    ENT = 0x0065
    DEL = 0x0063
    CE = 0x0069

    PROG_Q = 0x006E

    NUM_BLOCK_0 = 0x006E
    NUM_BLOCK_1 = 0x0070
    NUM_BLOCK_2 = 0x0074
    NUM_BLOCK_3 = 0x007D
    NUM_BLOCK_4 = 0x0071
    NUM_BLOCK_5 = 0x0075
    NUM_BLOCK_6 = 0x007E
    NUM_BLOCK_7 = 0x0072
    NUM_BLOCK_8 = 0x0076
    NUM_BLOCK_9 = 0x007F

    MODE_MANUAL = 0x0048
    MODE_HANDWHEEL = 0x0040
    MODE_SINGLE_STEP = 0x004A
    MODE_POS_HAND = 0x0049
    MODE_PGM_SIMULATION = 0x0041
    MODE_AUTOMATIC = 0x004B
    MODE_PGM_EDIT = 0x004C

    FN = 0x006E
    DECIMAL_POINT = 0x0073
    ACTPOS = 0x0064
    MOD_DIALOG = 0x0042

    ANGULAR_AXIS_1 = 0x006A
    ANGULAR_AXIS_2 = 0x004F
    AXIS_Z = 0x006B
    AXIS_Y = 0x006C
    AXIS_X = 0x006D
    TOGGEL_POLAR = 0x0043

    PROG_TOUCH_PROBE = 0x004E
    PROG_RR = 0x0057
    PROG_RL = 0x0056
    PROG_LBL_CALL = 0x005E
    PROG_STOP = 0x0060
    PROG_C = 0x003F

    PROG_LBL = 0x005D
    PROG_CC = 0x003E
    PROG_PGM_CALL = 0x0045
    PROG_TOOL_CALL = 0x0055
    PROG_CYC_CALL = 0x005C
    PROG_RND = 0x003D
    PROG_CR = 0x0047
    PROG_BLK_FORM = 0x00FF
    PROG_TOOL_DEF = 0x0054
    PROG_CYC_DEF = 0x005B
    PROG_CT = 0x004D
    PROG_L = 0x003C
    PROG_APPR_DEP = 0x0078
    PROG_CHF = 0x003A

    PGMMGT = 0x0061
    TOGGEL_INC = 0x0044

    CL_PGM = 0x0062
    PGM_NR = 0x003B

    ARROW_LEFT = 0x0059
    ARROW_DOWN = 0x0067
    ARROW_UP = 0x0058
    ARROW_RIGHT = 0x005A
    GOTO = 0x0066

    # soft key: low byte = 0x50, high byte = key number
    BOTTOM_SK0 = 0x0051
    BOTTOM_SK1 = 0x0151
    BOTTOM_SK2 = 0x0251
    BOTTOM_SK3 = 0x0351
    BOTTOM_SK4 = 0x0451
    BOTTOM_SK5 = 0x0551
    BOTTOM_SK6 = 0x0651
    BOTTOM_SK7 = 0x0751

    SK_PREVIOUS = 0x0851
    SK_NEXT = 0x0A51

    # screen keys: low byte = 0x52
    CHANGE_SCREEN = 0x0052
    SPLIT_SCREEN = 0x0152


class CMD(str, Enum):
    """Enum of all known LSV2 command telegrams"""

    A_LG = "A_LG"
    """A_LG: used to gain access to certain parts of the control, followed by a logon name and an optional password.
    requires no login priviliege"""

    A_LO = "A_LO"
    """A_LO: used to drop access to certain parts of the control, followed by an optional logon name.
    requires any login priviliege"""

    C_CC = "C_CC"
    """C_CC: used to set system commands"""

    C_DC = "C_DC"
    """C_DC: change the working directory for future file operations, followed by a null terminated string.
    requires FILE login priviliege"""

    # C_DS = "C_DS" # C_DS: found via bruteforce test, purpose unknown!

    C_DT = "C_DT"
    """set date and time.
    requires DIAGNOSTICS login priviliege"""

    C_DD = "C_DD"
    """C_DD: delete a directory, followed by a null terminated string.
    requires FILE login priviliege"""

    C_DM = "C_DM"
    """C_DM: create a new directory, followed by a null terminated string.
    requires FILE login priviliege"""

    C_EK = "C_EK"
    """C_EK: send key code to control. Behaves as if the associated key was pressed on the keyboard.
    requires DIAGNOSTICS or MONITOR login priviliege"""

    C_FA = "C_FA"
    """change file attribute.
    requires FILE login priviliege"""

    C_FC = "C_FC"
    """C_FC: local file copy from current directory, filename + null + target path + null.
    requires FILE login priviliege"""

    C_FD = "C_FD"
    """C_FD: delete a file, followed by a null terminated string.
    requires FILE login priviliege"""

    C_FL = "C_FL"
    """C_FL: send a file to the control, followed by a null terminated with the filename string.
    requires FILE login priviliege"""

    C_FR = "C_FR"
    """C_FR: move local file from current directory, filename + null + target path + null.
    requires FILE login priviliege"""

    # C_GC = "C_GC" # found via bruteforce test, purpose unknown!

    C_LK = "C_LK"
    """C_LK: lock and unlock keyboard input on control, followed by a switch if lock or unlock.
    requires DIAGNOSTICS or MONITOR login priviliege"""

    # C_MB = "C_MB" # found via bruteforce test, purpose unknown!

    C_MC = "C_MC"
    """C_MC: set machine parameter, followed by flags, name and value
    requires PLCDEBUG login privilege"""

    # C_OP = 'C_OP' # found via bruteforce test, purpose unknown! -> Timeout

    C_ST = "C_ST"
    """C_ST: set status. can only change status for active logins.
    requires any login priviliege"""

    # C_TP = "C_TP" # found via bruteforce test, purpose unknown!

    R_CD = "R_CD"
    """request character set.
    requires MONITOR login priviliege"""

    R_CI = "R_CI"
    """R_CI: TODO something to do with scope"""

    R_DI = "R_DI"
    """R_DI: directory info - read info about the selected directory.
    requires FILE login priviliege"""

    R_DP = "R_DP"
    """R_DP: read data from data path, only available on iTNC530 starting with 34049x 03 and 60642x 01"""

    R_DR = "R_DR"
    """R_DR: get info about directory content.
    requires FILE login priviliege"""

    # R_DS = 'R_DS' # found via bruteforce test, purpose unknown!

    R_DT = "R_DT"
    """request date/time.
    requires DIAGNOSTICS login priviliege"""

    R_FI = "R_FI"
    """R_FI: file info - read info about a file, followed by a null terminated string.
    requires FILE login priviliege. """

    R_FL = "R_FL"
    """R_FL: load a file from the control, followed by a null terminated string with the filename.
    requires FILE login priviliege"""

    R_FO = "R_FO"
    """request font definition.
    requires MONITOR login priviliege"""

    # R_IN = "R_IN" # found via bruteforce test, purpose unknown!

    R_LB = "R_LB"
    """request log buffer.
    requires DIAGNOSTICS login priviliege"""

    R_MB = "R_MB"
    """R_MB: read value from PLC memory, followed by four bytes of address and one byte of count.
    requires INSPECT (PLCDEBUG??) login priviliege"""

    R_MC = "R_MC"
    """R_MC: read machine parameter, followed by a null terminated string with the parameter number/path.
    requires INSPECT login priviliege"""

    R_MP = "R_MP"
    """R_MP: read machine parameter.
    requires INSPECT login priviliege"""

    R_OC = "R_OC"
    """R_OC: TODO: read something to do with scope"""
    R_OD = "R_OD"
    """R_OD: TODO: read something to do with scope"""
    R_OP = "R_OP"
    """R_OP: TODO: read something to do with scope"""

    # R_OD = "R_OD" # found via bruteforce test, purpose unknown!
    # R_OH = "R_OH" # found via bruteforce test, purpose unknown!
    # R_OI = "R_OI" # found via bruteforce test, purpose unknown!

    R_PD = "R_PD"
    """request palet definition.
    requires FILE or MONITOR login priviliege"""

    R_PR = "R_PR"
    """R_PR: read parameter from the control.
    requires INSPECT login priviliege"""

    R_RI = "R_RI"
    """R_RI: read info about the current state of the control ???, followed by a 16bit number to select which information (20 - 26??)"""

    R_RS = "R_RS"
    """R_RS: request register status.
    requires INSPECT login priviliege"""

    R_SD = "R_SD"
    """request screen dump.
    requires FILE login priviliege"""

    R_SE = "R_SE"
    """request screen window element info.
    requires MONITOR login priviliege"""

    R_SP = "R_SP"
    """request screen palet info.
    requires MONITOR login priviliege"""

    R_SS = "R_SS"
    """request active screen.
    requires INSPECT login priviliege"""

    R_ST = "R_ST"
    """R_ST: request remote status.
    requires any login priviliege"""

    R_SW = "R_SW"
    """request screen window info.
    requires MONITOR login priviliege"""

    R_VR = "R_VR"
    """R_VR: read general info about the control itself.
    requires INSPECT login priviliege"""

    R_WD = "R_WD"
    """request window definition.
    requires MONITOR login priviliege"""

    NONE = "NONE"
    """not a valid command but used internally"""


class RSP(str, Enum):
    """Enum of all known response telegrams"""

    T_OK = "T_OK"
    """T_OK: signals that the last transaction was completed, no additional data is sent?"""

    T_ER = "T_ER"
    """T_ER: signals that An error occurred during the last transaction, followed by An error code?"""

    T_FD = "T_FD"
    """T_FD: signals that all file data has been sent and the transfer is finished"""

    T_BD = "T_BD"
    """T_BD: signals that An error occurred during the file transfer, it is followed by more data"""

    M_CC = "M_CC"
    """M_CC: signals that a poeration some king of operation was completed that took some time to complete, ??? response to C_CC??"""

    S_CI = "S_CI"
    """S_CI: TODO something to do with scope"""

    S_DI = "S_DI"
    """S_DI: signals that the command R_DI was accepted, it is followed by more data"""

    S_DT = "S_DT"
    """S_DT: TODO something to do with date/time and scope?"""

    S_DP = "S_DP"
    """S_DP: signals that the command R_DP was accepted, is followed by data value"""

    S_DR = "S_DR"
    """S_DR: ??? signals that the command R_DR was accepted, it is followed by more data"""

    S_FI = "S_FI"
    """S_FI: signals that the command R_FI was accepted, it is followed by more data"""

    S_FL = "S_FL"
    """S_FL: used to transfer blocks of file data to the control, signals that the command R_FL was accepted, it is followed by more data"""

    # S_IN = "S_IN"
    # S_IN: found via bruteforce test, signals that the command R_IN was accepted, purpose unknown!

    S_MB = "S_MB"
    """S_MB: signals that the command R_MB to read plc memory was accepted, is followed by the actual data"""

    S_MC = "S_MC"
    """S_MC: signal that the command R_MC to read machine parameter was accepted, is followed by the actual data"""

    S_OC = "S_OC"
    """S_OC: TODO signal that has something to do with the scope"""
    S_OD = "S_OD"
    """S_OP: TODO: read something to do with scope"""
    S_OP = "S_OP"
    """S_OP: TODO signal that has something to do with the scope"""

    S_PR = "S_PR"
    """S_PR: signals that the command R_PR and the parameter was accepted, it is followed by more data"""

    S_RI = "S_RI"
    """S_RI: signals that the command R_RI was accepted, it is followed by more data"""

    S_ST = "S_ST"
    """S_ST: signals that the command R_ST was accepted, request remote status"""

    S_VR = "S_VR"
    """S_VR: signals that the command R_VR was accepted, it is followed by more data"""

    NONE = "NONE"
    """not a valid response but used internally to signal that no response was received or should be sent"""

    UNKNOWN = "UNKN"
    """not a valid response but used internally to signal an unknown response was received"""


class ParCCC(IntEnum):
    """enum for telegram C_CC / SetSysCmd"""

    RESET_TNC = 1
    STOP_TIMEUPDATE = 2
    SET_BUF1024 = 3
    SET_BUF512 = 4
    SET_BUF2048 = 5
    SET_BUF3072 = 6
    SET_BUF4096 = 7
    RESET_DNC = 8
    RESET_LSV2 = 9
    """not implemented"""

    UPDATE_TNCOPT = 10
    PUSH_PRESET_INTO_LOG = 11
    SCREENDUMP = 12
    ACTIVATE_PLCPGM = 13
    """parameter: file name"""
    OBSERVE_ADD_FILE = 15
    """parameter: file name"""
    OBSERVE_REMOVE_FILE = 16
    """parameter: file name"""
    OBSERVE_REMOVE_ALL = 17
    ACTIVATE_MFSK = 18
    """set behavior of C_FL: T_FD will be akknowleged with T_OK or T_ER"""
    SECURE_FILE_SEND = 19
    DELETE_TABLE_ENTRY = 20
    """generate operations log file, parameters: filename, start time and date"""
    GENERATE_OP_LOG = 27


class ParRVR(IntEnum):
    """enum of parameters used with command R_VR"""

    CONTROL = 1
    NC_VERSION = 2
    PLC_VERSION = 3
    OPTIONS = 4
    ID = 5
    RELEASE_TYPE = 6
    SPLC_VERSION = 7


class ParRRI(IntEnum):
    """enum of parameters used with command R_RI"""

    AXIS_LOCATION = 22
    EXEC_STATE = 23
    SELECTED_PGM = 24
    OVERRIDE = 25
    PGM_STATE = 26
    FIRST_ERROR = 27
    NEXT_ERROR = 28
    CURRENT_TOOL = 51


class ParRDR(IntEnum):
    """enum of parameters used with command R_DR"""

    SINGLE = 0x00
    """mode switch to only read one entry at a time"""

    MULTI = 0x01
    """mode switch to read multiple entries at a time, needs larger telegram size"""

    DRIVES = 0x02
    """mode switch to read drive information"""


class ChannelType(IntEnum):
    """Enum of scope channel types"""

    UNKNOWN = -1
    TYPE0 = 0
    TYPE1 = 1
    TYPE2 = 2
    TYPE3 = 3
    TYPE4 = 4
    TYPE5 = 10

    @classmethod
    def has_value(cls, value):
        return value in set(item.value for item in ChannelType)


class ChannelSignal():
    s_actual_X = 0
    s_actual_Y = 1
    s_actual_Z = 2
    s_actual_B = 3
    s_actual_C = 4
    s_actual_5 = 5
    s_actual_6 = 6
    s_actual_7 = 7
    s_actual_8 = 8
    s_actual_9 = 9
    s_actual_S = 10
    s_nominal_X = 11
    s_nominal_Y = 12
    s_nominal_Z = 13
    s_nominal_B = 14
    s_nominal_C = 15
    s_nominal_5 = 16
    s_nominal_6 = 17
    s_nominal_7 = 18
    s_nominal_8 = 19
    s_nominal_9 = 20
    s_nominal_S = 21
    s_diff_X = 22
    s_diff_Y = 23
    s_diff_Z = 24
    s_diff_B = 25
    s_diff_C = 26
    s_diff_5 = 27
    s_diff_6 = 28
    s_diff_7 = 29
    s_diff_8 = 30
    s_diff_9 = 31
    s_diff_S = 32
    Volt_analog_X = 33
    Volt_analog_Y = 34
    Volt_analog_Z = 35
    Volt_analog_B = 36
    Volt_analog_C = 37
    Volt_analog_5 = 38
    Volt_analog_6 = 39
    Volt_analog_7 = 40
    Volt_analog_8 = 41
    Volt_analog_9 = 42
    Volt_analog_S = 43
    v_actual_X = 44
    v_actual_Y = 45
    v_actual_Z = 46
    v_actual_B = 47
    v_actual_C = 48
    v_actual_5 = 49
    v_actual_6 = 50
    v_actual_7 = 51
    v_actual_8 = 52
    v_actual_9 = 53
    v_actual_S = 54
    v_nominal_X = 55
    v_nominal_Y = 56
    v_nominal_Z = 57
    v_nominal_B = 58
    v_nominal_C = 59
    v_nominal_5 = 60
    v_nominal_6 = 61
    v_nominal_7 = 62
    v_nominal_8 = 63
    v_nominal_9 = 64
    v_nominal_S = 65
    Feed_rate_F = 66
    Position_A_X = 67
    Position_A_Y = 68
    Position_A_Z = 69
    Position_A_B = 70
    Position_A_C = 71
    Position_A_5 = 72
    Position_A_6 = 73
    Position_A_7 = 74
    Position_A_8 = 75
    Position_A_9 = 76
    Position_A_S = 77
    Position_B_X = 78
    Position_B_Y = 79
    Position_B_Z = 80
    Position_B_B = 81
    Position_B_C = 82
    Position_B_5 = 83
    Position_B_6 = 84
    Position_B_7 = 85
    Position_B_8 = 86
    Position_B_9 = 87
    Position_B_S = 88
    v_act_rpm_X = 89
    v_act_rpm_Y = 90
    v_act_rpm_Z = 91
    v_act_rpm_B = 92
    v_act_rpm_C = 93
    v_act_rpm_5 = 94
    v_act_rpm_6 = 95
    v_act_rpm_7 = 96
    v_act_rpm_8 = 97
    v_act_rpm_9 = 98
    v_act_rpm_S = 99
    v_nom_rpm_X = 100
    v_nom_rpm_Y = 101
    v_nom_rpm_Z = 102
    v_nom_rpm_B = 103
    v_nom_rpm_C = 104
    v_nom_rpm_5 = 105
    v_nom_rpm_6 = 106
    v_nom_rpm_7 = 107
    v_nom_rpm_8 = 108
    v_nom_rpm_9 = 109
    v_nom_rpm_S = 110
    I_int_rpm_X = 111
    I_int_rpm_Y = 112
    I_int_rpm_Z = 113
    I_int_rpm_B = 114
    I_int_rpm_C = 115
    I_int_rpm_5 = 116
    I_int_rpm_6 = 117
    I_int_rpm_7 = 118
    I_int_rpm_8 = 119
    I_int_rpm_9 = 120
    I_int_rpm_S = 121
    I_nominal_X = 122
    I_nominal_Y = 123
    I_nominal_Z = 124
    I_nominal_B = 125
    I_nominal_C = 126
    I_nominal_5 = 127
    I_nominal_6 = 128
    I_nominal_7 = 129
    I_nominal_8 = 130
    I_nominal_9 = 131
    I_nominal_S = 132
    PLC_M = 133
    PLC_T = 134
    PLC_C = 135
    PLC_I = 136
    PLC_O = 137
    PLC_B = 138
    PLC_W = 139
    PLC_D = 140
    PLC_IB = 141
    PLC_IW = 142
    PLC_ID = 143
    PLC_OB = 144
    PLC_OW = 145
    PLC_OD = 146
    a_nominal_X = 147
    a_nominal_Y = 148
    a_nominal_Z = 149
    a_nominal_B = 150
    a_nominal_C = 151
    a_nominal_5 = 152
    a_nominal_6 = 153
    a_nominal_7 = 154
    a_nominal_8 = 155
    a_nominal_9 = 156
    a_nominal_S = 157
    r_nominal_X = 158
    r_nominal_Y = 159
    r_nominal_Z = 160
    r_nominal_B = 161
    r_nominal_C = 162
    r_nominal_5 = 163
    r_nominal_6 = 164
    r_nominal_7 = 165
    r_nominal_8 = 166
    r_nominal_9 = 167
    r_nominal_S = 168
    Pos_Diff_X = 169
    Pos_Diff_Y = 170
    Pos_Diff_Z = 171
    Pos_Diff_B = 172
    Pos_Diff_C = 173
    Pos_Diff_5 = 174
    Pos_Diff_6 = 175
    Pos_Diff_7 = 176
    Pos_Diff_8 = 177
    Pos_Diff_9 = 178
    Pos_Diff_S = 179
    a_actual_X = 180
    a_actual_Y = 181
    a_actual_Z = 182
    a_actual_B = 183
    a_actual_C = 184
    a_actual_5 = 185
    a_actual_6 = 186
    a_actual_7 = 187
    a_actual_8 = 188
    a_actual_9 = 189
    a_actual_S = 190
    r_actual_X = 191
    r_actual_Y = 192
    r_actual_Z = 193
    r_actual_B = 194
    r_actual_C = 195
    r_actual_5 = 196
    r_actual_6 = 197
    r_actual_7 = 198
    r_actual_8 = 199
    r_actual_9 = 200
    r_actual_S = 201
    I2_t_mot_X = 202
    I2_t_mot_Y = 203
    I2_t_mot_Z = 204
    I2_t_mot_B = 205
    I2_t_mot_C = 206
    I2_t_mot_5 = 207
    I2_t_mot_6 = 208
    I2_t_mot_7 = 209
    I2_t_mot_8 = 210
    I2_t_mot_9 = 211
    I2_t_mot_S = 212
    I2_t_p_m_X = 213
    I2_t_p_m_Y = 214
    I2_t_p_m_Z = 215
    I2_t_p_m_B = 216
    I2_t_p_m_C = 217
    I2_t_p_m_5 = 218
    I2_t_p_m_6 = 219
    I2_t_p_m_7 = 220
    I2_t_p_m_8 = 221
    I2_t_p_m_9 = 222
    I2_t_p_m_S = 223
    Utilization_X =224
    Utilization_Y =225
    Utilization_Z =226
    Utilization_B =227
    Utilization_C =228
    Utilization_5 =229
    Utilization_6 =230
    Utilization_7 =231
    Utilization_8 =232
    Utilization_9 =233
    Utilization_S =234
    Block_no = 235
    Gantry_dif_X = 236
    Gantry_dif_Y = 237
    Gantry_dif_Z = 238
    Gantry_dif_B = 239
    Gantry_dif_C = 240
    Gantry_dif_5 = 241
    Gantry_dif_6 = 242
    Gantry_dif_7 = 243
    Gantry_dif_8 = 244
    Gantry_dif_9 = 245
    Gantry_dif_S = 246
    U_nominal_X = 247
    U_nominal_Y = 248
    U_nominal_Z = 249
    U_nominal_B = 250
    U_nominal_C = 251
    U_nominal_5 = 252
    U_nominal_6 = 253
    U_nominal_7 = 254
    U_nominal_8 = 255
    U_nominal_9 = 256
    U_nominal_S = 257
    P_mech_X = 258
    P_mech_Y = 259
    P_mech_Z = 260
    P_mech_B = 261
    P_mech_C = 262
    P_mech_5 = 263
    P_mech_6 = 264
    P_mech_7 = 265
    P_mech_8 = 266
    P_mech_9 = 267
    P_mech_S = 268
    P_elec_X = 269
    P_elec_Y = 270
    P_elec_Z = 271
    P_elec_B = 272
    P_elec_C = 273
    P_elec_5 = 274
    P_elec_6 = 275
    P_elec_7 = 276
    P_elec_8 = 277
    P_elec_9 = 278
    P_elec_S = 279
    M_actual_X = 280
    M_actual_Y = 281
    M_actual_Z = 282
    M_actual_B = 283
    M_actual_C = 284
    M_actual_5 = 285
    M_actual_6 = 286
    M_actual_7 = 287
    M_actual_8 = 288
    M_actual_9 = 289
    M_actual_S = 290
    s_noml_f_X = 291
    s_noml_f_Y = 292
    s_noml_f_Z = 293
    s_noml_f_B = 294
    s_noml_f_C = 295
    s_noml_f_5 = 296
    s_noml_f_6 = 297
    s_noml_f_7 = 298
    s_noml_f_8 = 299
    s_noml_f_9 = 300
    s_noml_f_S = 301
    DSP_debug_X =302
    DSP_debug_Y =303
    DSP_debug_Z =304
    DSP_debug_B =305
    DSP_debug_C =306
    DSP_debug_5 =307
    DSP_debug_6 =308
    DSP_debug_7 =309
    DSP_debug_8 =310
    DSP_debug_9 =311
    DSP_debug_S =312
    Deviation_X =313
    Deviation_Y =314
    Deviation_Z =315
    Deviation_B =316
    Deviation_C =317
    Deviation_5 =318
    Deviation_6 =319
    Deviation_7 =320
    Deviation_8 =321
    Deviation_9 =322
    Deviation_S =323
    F_TCPM = 324
    Int_diagn = 325
    DC_link_P_X = 326
    DC_link_P_Y = 327
    DC_link_P_Z = 328
    DC_link_P_B = 329
    DC_link_P_C = 330
    DC_link_P_5 = 331
    DC_link_P_6 = 332
    DC_link_P_7 = 333
    DC_link_P_8 = 334
    DC_link_P_9 = 335
    DC_link_P_S = 336
    Amplitude_X = 337
    Amplitude_Y = 338
    Amplitude_Z = 339
    Amplitude_B = 340
    Amplitude_C = 341
    Amplitude_5 = 342
    Amplitude_6 = 343
    Amplitude_7 = 344
    Amplitude_8 = 345
    Amplitude_9 = 346
    Amplitude_S = 347
    Motor_A_X =348
    Motor_A_Y =349
    Motor_A_Z =350
    Motor_A_B =351
    Motor_A_C =352
    Motor_A_5 =353
    Motor_A_6 =354
    Motor_A_7 =355
    Motor_A_8 =356
    Motor_A_9 =357
    Motor_A_S =358
    Motor_B_X =359
    Motor_B_Y =360
    Motor_B_Z =361
    Motor_B_B =362
    Motor_B_C =363
    Motor_B_5 =364
    Motor_B_6 =365
    Motor_B_7 =366
    Motor_B_8 =367
    Motor_B_9 =368
    Motor_B_S =369
    CC_DIAG = 370
    SPLC_M = 371
    SPLC_T = 372
    SPLC_C = 373
    SPLC_I = 374
    SPLC_O = 375
    SPLC_B = 376
    SPLC_W = 377
    SPLC_D = 378
    SPLC_IB = 379
    SPLC_IW = 380
    SPLC_ID = 381
    SPLC_OB = 382
    SPLC_OW = 383
    SPLC_OD = 384
    SPLC_CC_M =385
    SPLC_CC_T =386
    SPLC_CC_C =387
    SPLC_CC_I =388
    SPLC_CC_O =389
    SPLC_CC_B =390
    SPLC_CC_W =391
    SPLC_CC_D =392
    SPLC_CC_IB = 393
    SPLC_CC_IW = 394
    SPLC_CC_ID = 395
    SPLC_CC_OB = 396
    SPLC_CC_OW = 397
    SPLC_CC_OD = 398
    compensat_X = 399
    compensat_Y = 400
    compensat_Z = 401
    compensat_B = 402
    compensat_C = 403
    compensat_5 = 404
    compensat_6 = 405
    compensat_7 = 406
    compensat_8 = 407
    compensat_9 = 408
    compensat_S = 409
    I_actual_X =410
    I_actual_Y =411
    I_actual_Z =412
    I_actual_B =413
    I_actual_C =414
    I_actual_5 =415
    I_actual_6 =416
    I_actual_7 =417
    I_actual_8 =418
    I_actual_9 =419
    I_actual_S =420
    Actl_Id_X = 421
    Actl_Id_Y = 422
    Actl_Id_Z = 423
    Actl_Id_B = 424
    Actl_Id_C = 425
    Actl_Id_5 = 426
    Actl_Id_6 = 427
    Actl_Id_7 = 428
    Actl_Id_8 = 429
    Actl_Id_9 = 430
    Actl_Id_S = 431
    Max_Iq_X = 432
    Max_Iq_Y = 433
    Max_Iq_Z = 434
    Max_Iq_B = 435
    Max_Iq_C = 436
    Max_Iq_5 = 437
    Max_Iq_6 = 438
    Max_Iq_7 = 439
    Max_Iq_8 = 440
    Max_Iq_9 = 441
    Max_Iq_S = 442
    KinComp_X =443
    KinComp_Y =444
    KinComp_Z =445
    KinComp_B =446
    KinComp_C =447
    KinComp_5 =448
    KinComp_6 =449
    KinComp_7 =450
    KinComp_8 =451
    KinComp_9 =452
    KinComp_S =453
    REF_X = 454
    REF_Y = 455
    REF_Z = 456
    REF_B = 457
    REF_C = 458
    REF_5 = 459
    REF_6 = 460
    REF_7 = 461
    REF_8 = 462
    REF_9 = 463
    REF_S = 464

    
    
