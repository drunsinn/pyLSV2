Extract from the LSV2-TOOLBOX user manual
=========================================

Thanks to the help of the user NeeXoo an official manual for something called the LSV2-TOOLBOX was
discovered. Since it is dated July 1993 it shows some differences between the implementation for
current controls and the controls that where around in 1993. Nevertheless here are some parts of
the document which might be of interest in the future.

The original document found by NeeXoo can be found on [yumpu.com](https://www.yumpu.com/de/document/read/18882603/-f-heidenhain).

Since the original document is in german, most of the translation was done using (deepl.com)[https://www.deepl.com]. Thanks for their
great free service!

LSV2-Telegrams
--------------
+--------------------------+-------+----------------------------+
| Commands                 | C_xx  | Command Telegram           |
+--------------------------+-------+----------------------------+
| Messages                 | M_xx  | Message Telegram           |
+--------------------------+-------+----------------------------+
| Messages to acknowledge  | X_xx  | Cross Message Telegram     |
+--------------------------+-------+----------------------------+
| Requests                 | R_xx  | Request Telegram           |
+--------------------------+-------+----------------------------+
| Transmit                 | S_xx  | Send Telegram              |
+--------------------------+-------+----------------------------+
| Transfer control         | T_xx  | Transmit Control Telegram  |
+--------------------------+-------+----------------------------+

Datatypes
---------
WORD (16 bit) and LONG (32 bit) data types are always transmitted in MOTOROLA format: The byte with the highest significance first,
the byte with the lowest significance last.

WORD (16 bit) and LONG (32 bit) data types are always placed at word boundaries in the telegram structure. If necessary
a dummy byte is inserted. This is necessary, because with software generation not all controllers have the WORD and
LONG data types between word boundaries (so-called word alignment).

If character strings (strings) such as file names are to be transmitted this is done as a zero terminated ASCII 
string. The string is always terminated with the zero byte (0x00) (Null terminated string).
Strings that do not have a fixed length are, if possible, placed at the end of the telegram. Only the actual
string (including zero byte) is transmitted. So there is no padding necessary.
If several character strings are to be transmitted as parameters in one telegram (e.g. for file renaming), these
are combined in a character field at the end of the telegram. Only the character strings (including the zero byte) are
entered without padding.

Important constants
-------------------
+---------------+------+------------------------------------------------------------------------------------------------------------------------------------------------+
| CMD LENGTH    | 4    | Length of the LSV2 telegram command identifier                                                                                                 |
+===============+======+================================================================================================================================================+
| MAXTELEGRAM   | 256  | maximum telegram length (effectively only 128 characters including command identifier)                                                         |
+---------------+------+------------------------------------------------------------------------------------------------------------------------------------------------+
| MAXERROR      | 256  | maximum number of error numbers                                                                                                                |
+---------------+------+------------------------------------------------------------------------------------------------------------------------------------------------+
| MAXPATH       | 80   | maximum file name length (including path)                                                                                                      |
+---------------+------+------------------------------------------------------------------------------------------------------------------------------------------------+
| MAXATTR       | 32   | maximum allowed number of attributes                                                                                                           |
+---------------+------+------------------------------------------------------------------------------------------------------------------------------------------------+
| MAXPASSWORD   | 16   | maximum password length                                                                                                                        |
+---------------+------+------------------------------------------------------------------------------------------------------------------------------------------------+
| MAXFILENAME   | 21   | maximum file name length (max. 16 characters for name, 1 character for file name extension "." and max. 3 characters for file name extension)  |
+---------------+------+------------------------------------------------------------------------------------------------------------------------------------------------+
| MAXMP         | 20   | maximum length of a machine parameter string                                                                                                   |
+---------------+------+------------------------------------------------------------------------------------------------------------------------------------------------+
| MAXVERSION    | 16   | maximum length of a version string                                                                                                             |
+---------------+------+------------------------------------------------------------------------------------------------------------------------------------------------+
| MAXDNCMSGSTR  | 128  | Maximum length of a DNC plain text message                                                                                                     |
+---------------+------+------------------------------------------------------------------------------------------------------------------------------------------------+


Overview of commands ordered by function
----------------------------------------
TBD


Overview of commands ordered by login
-------------------------------------
+-------------+----------------------+-----------------------------------+
| Login       | Command              | Description                       |
+=============+======================+===================================+
| none        | A_LG                 | Login                             |
+-------------+----------------------+-----------------------------------+
| any         | A_LO                 | Logout                            |
+-------------+----------------------+-----------------------------------+
| any         | R_ST                 | Request Remote Status             |
+-------------+----------------------+-----------------------------------+
| any         | C_ST                 | Set Status                        |
+-------------+----------------------+-----------------------------------+
| INSPECT     | R_VR                 | Request Version                   |
+-------------+----------------------+-----------------------------------+
| INSPECT     | R_PR                 | Request Systemparameters          |
+-------------+----------------------+-----------------------------------+
| INSPECT     | R_MB                 | Request Memory Block              |
+-------------+----------------------+-----------------------------------+
| INSPECT     | R_MP                 | Request Machine Parameter         |
+-------------+----------------------+-----------------------------------+
| INSPECT     | R_RS                 | Request Register Status           |
+-------------+----------------------+-----------------------------------+
| INSPECT     | R_SS                 | Request Active Screen             |
+-------------+----------------------+-----------------------------------+
| DIAGNOSTICS | R_LB                 | Request Logbuffer                 |
+-------------+----------------------+-----------------------------------+
| DIAGNOSTICS | R_DT                 | Request Date/Time                 |
+-------------+----------------------+-----------------------------------+
| DIAGNOSTICS | C_DT                 | Set Date / Time                   |
+-------------+----------------------+-----------------------------------+
| DIAGNOSTICS | C_LK                 | Lock/Unlock NC Keys               |
+-------------+----------------------+-----------------------------------+
| DIAGNOSTICS | C_EK                 | Emulate Keypress                  |
+-------------+----------------------+-----------------------------------+
| DIAGNOSTICS | all of login INSPECT |                                   |
+-------------+----------------------+-----------------------------------+
| FILE        | R_DI                 | Request Directory Information     |
+-------------+----------------------+-----------------------------------+
| FILE        | R_DR                 | Request Directory                 |
+-------------+----------------------+-----------------------------------+
| FILE        | R_FL                 | Request File                      |
+-------------+----------------------+-----------------------------------+
| FILE        | R_PD                 | Request Palettedefinition         |
+-------------+----------------------+-----------------------------------+
| FILE        | R_SD                 | Request Screendump                |
+-------------+----------------------+-----------------------------------+
| FILE        | S_DI                 | Send Directory Information        |
+-------------+----------------------+-----------------------------------+
| FILE        | S_DR                 | Send Directory Block              |
+-------------+----------------------+-----------------------------------+
| FILE        | S_FL                 | Send File Block                   |
+-------------+----------------------+-----------------------------------+
| FILE        | C_FD                 | Delete File                       |
+-------------+----------------------+-----------------------------------+
| FILE        | C_FR                 | Rename File                       |
+-------------+----------------------+-----------------------------------+
| FILE        | C_FC                 | Copy File                         |
+-------------+----------------------+-----------------------------------+
| FILE        | C_FA                 | Change File Attribute             |
+-------------+----------------------+-----------------------------------+
| FILE        | C_DC                 | Change Current Directory          |
+-------------+----------------------+-----------------------------------+
| FILE        | C_FL                 | Load File                         |
+-------------+----------------------+-----------------------------------+
| FILE        | all of login INSPECT |                                   |
+-------------+----------------------+-----------------------------------+
| DNC         | C_NC                 | Load NC File (DNC)                |
+-------------+----------------------+-----------------------------------+
| DNC         | C_CN                 | Cancel DNC Filetransfer           |
+-------------+----------------------+-----------------------------------+
| DNC         | X_PC                 | DNC Message to/from PLC           |
+-------------+----------------------+-----------------------------------+
| DNC         | X_OK                 | Handshake Message                 |
+-------------+----------------------+-----------------------------------+
| DNC         | X_ER                 | Handshake Message                 |
+-------------+----------------------+-----------------------------------+
| MONITOR     | R_WD                 | Request window definition         |
+-------------+----------------------+-----------------------------------+
| MONITOR     | R_PD                 | Request palette definition        |
+-------------+----------------------+-----------------------------------+
| MONITOR     | R_FO                 | Request Fontdefinition            |
+-------------+----------------------+-----------------------------------+
| MONITOR     | R_CD                 | Request Characterset              |
+-------------+----------------------+-----------------------------------+
| MONITOR     | R_SW                 | Request Screen Window Info        |
+-------------+----------------------+-----------------------------------+
| MONITOR     | R_SE                 | Request Screenwindow Element Info |
+-------------+----------------------+-----------------------------------+
| MONITOR     | R_SP                 | Request Screenpalette Info        |
+-------------+----------------------+-----------------------------------+
| MONITOR     | C_LK                 | Lock/Unlock NC Keys               |
+-------------+----------------------+-----------------------------------+
| MONITOR     | C_EK                 | Emulate Keypress                  |
+-------------+----------------------+-----------------------------------+
| MONITOR     | all of login INSPECT |                                   |
+-------------+----------------------+-----------------------------------+

