#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Constant values used in LSV2"""
from enum import Enum, IntEnum

# #: files system attributes
# FS_ENTRY_IS_HIDDEN = 0x08
# FS_ENTRY_IS_DRIVE = 0x10
# FS_ENTRY_IS_DIRECTORY = 0x20
# FS_ENTRY_IS_PROTCTED = 0x40
# FS_ENTRY_IS_IN_USE = 0x80

#: enable binary file transfer for C_FL and R_FL
MODE_BINARY = 0x01

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


class LSV2Err(IntEnum):
    """Enum for LSV2 protocol error numbers
    range 0 - 19: protocol or transmission errors
    range 20 - 99: telegram errors
    range 100 - 200: block transfer errors
    """

    LSV2_OK = 0

    # reciving
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
    PROG_CYC_CAL = PROG_CYC_CALL  # TODO typo
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

    PROG_TOUCH_PROBE = 0x004E  # TODO
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

    Cl_Pgm = 0x0062  # TODO
    Pgm_Nr = 0x003B  # TODO

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
    """

    # C_OP = 'C_OP' # found via bruteforce test, purpose unknown! -> Timeout

    C_ST = "C_ST"
    """C_ST: set status. can only change status for active logins.
    requires any login priviliege"""

    # C_TP = "C_TP" # found via bruteforce test, purpose unknown!

    R_CD = "R_CD"
    """request character set.
    requires MONITOR login priviliege"""

    # R_CI = "R_CI"  # found via bruteforce test, purpose unknown!

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

    # R_OC = "R_OC" # found via bruteforce test, purpose unknown!
    # R_OD = "R_OD" # found via bruteforce test, purpose unknown!
    # R_OH = "R_OH" # found via bruteforce test, purpose unknown!
    # R_OI = "R_OI" # found via bruteforce test, purpose unknown!

    R_PD = "R_PD"
    """request palet definiton.
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
    """request window definiton.
    requires MONITOR login priviliege"""


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

    S_DI = "S_DI"
    """S_DI: signals that the command R_DI was accepted, it is followed by more data"""

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

    S_PR = "S_PR"
    """S_PR: signals that the command R_PR and the parameter was accepted, it is followed by more data"""

    S_RI = "S_RI"
    """S_RI: signals that the command R_RI was accepted, it is followed by more data"""

    S_ST = "S_ST"
    """S_ST: signals that the command R_ST was accepted, request remote status"""

    S_VR = "S_VR"
    """S_VR: signals that the command R_VR was accepted, it is followed by more data"""


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
