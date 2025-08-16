Findings on LSV2
================
This document is a collection of all the information that was discovered while developing this library.

Differences between different control versions
----------------------------------------------
Some functions are only available on certain controls and/or versions of the software. 

+---------------------------+------------------------+------------------+--------------------------+
|                           | TNC                    | iTNC             | CNCpilot                 |
+===========================+========================+==================+==========================+
| Tool Table                | TNC:/table/tool.t      | TNC:/TOOL.T      |                          |
+---------------------------+------------------------+------------------+--------------------------+
| Pocket Table              | TNC:/table/tool_p.tch  | TNC:/TOOL_P.TCH  | TNC:/table/ToolAllo.tch  |
+---------------------------+------------------------+------------------+--------------------------+
| R_RI: current tool (51)   | no                     | yes              | no                       |
+---------------------------+------------------------+------------------+--------------------------+
| R_RI: error msg (27, 28)  | no                     | yes              | no                       |
+---------------------------+------------------------+------------------+--------------------------+

Information on the protocol based on reverse engineering and prior work
-----------------------------------------------------------------------
Each LSV2 telegram starts with a 32 bit length value followed by a command string consisting of exactly 4 characters. The length value does not include the command string, a telegram with only a command and no additional data will have a length value of 0x0000.
If additional data has to be sent after the command string the value 0x00 is used as a separator.
All values are transmitted with big-endian byte order.

File Info
---------
By using the command ``R_FI`` followed by a valid file path, the control responds with information about this file. This includes the file size, the unix-date and the filename.
The message also contains some additional bytes which purpose is not yet confirmed. These bytes are probably attributes and/or access rights.

Directory info
--------------
The command for reading the content of a directory seems to support an additional parameter. With 0x01 sent after the command, the control sends all entries at once and not one entry per packet. ``R_DI`` 0x01 -> all info at once and not in separate packets

The directory information has also not been completely decoded yet. It contains the full path of the folder and a lot of zero bytes. By comparing results from different controls and directories it was determined that there seem to be a list of four byte-keys. their purpose is not yet known.
The first 4 bytes might have something to do with the size but it is always reported as 0xFF FF FF FF which would decode to 4,2 Gbyte. It might also be an indicator of the remaining free size of the disk.

Machine State
-------------
Based on discussion [here](https://github.com/tfischer73/Eclipse-Plugin-Heidenhain/issues/1)

Login with INSPECT::

   > R_RI 0x0015 (21) -> you can read the X,Y,Z Axis.

Login with DN::

   > R_RI 0x0018 (24) -> you can read the name of the current program in execution.

Login with DNC::

   > R_RI 0x001A (26) -> you can read the current program status

The states of program can be:

+--------+----------------+
| Value  | Meaning        |
+========+================+
| 0      | Started        |
+--------+----------------+
| 1      | Stopped        |
+--------+----------------+
| 2      | Finished       |
+--------+----------------+
| 3      | Cancelled      |
+--------+----------------+
| 4      | Interrupted    |
+--------+----------------+
| 5      | Error          |
+--------+----------------+
| 6      | Error Cleared  |
+--------+----------------+
| 7      | Idle           |
+--------+----------------+
| 8      | Undefined      |
+--------+----------------+

DNC login is only possible if the option is set on the control, without the option you get an error when trying to login with DNC.

Creating a log file - not implemented
-------------------------------------
By recording the communiction with Wireshark between the control and TNCremo the following sequence was accired.

::

   >....R_ST
   <....S_ST............
   >....C_ST............
   <....T_OK
   >...%C_CC..operation.log;12.09.2020;00:00:00;.
   <....T_OK
   <....M_CC...d 0x00 0x1b 0x00 0x64
   >....C_ST............
   <....T_OK
   >....R_FLTNC:\operation.log.
   <....S_FLOperation Logbook Version 1.0.Sy..

To trigger the generation of the log file, the telegram ``C_CC`` with command 27 is used. The parameters contain the filename of the log file an the start-date and time for the log entries.
This is to acknowledge with a ``T_OK``. After some time another telegram is receive: ``M_CC`` with data 0x00 1b 00 64. This seems to be the signal that the log file was created successfully and is ready to be copied.
Afterwards a regular file copy takes place.

File transfer
-------------
Transfer of files can happen in binary or ASCII mode. To enable binary mode, add 0x01 after the filename. In TNCremo you can find a list of file types for which binary mode is recommended.
The functions :py:meth:`pyLSV2.LSV2.recive_file` and :py:meth:`pyLSV2.LSV2.send_file` can be configured with the parameter `binary_mode`.

Scope
-----
LSV2 also includes functions to record live data in a style similar to an osziloskope. The OEM software is called TNCscope.
By analysing the traffic it was possible to include at least a subset of protocol necessary to emulate TNCscope. More modern conterols seem to require some special encryption, pyLSV2 therfor only supports the scope* functions for iTNC controls.
Reading of data begins by first reading the available signals from the control and selecting which ones are of interest. Each type of signal has a different interval value which is the minimum time step readings can be taken.
After selecting the signals, the interval and the number of readings the signals can be recorded.

::

   availible_signals = con.read_scope_channels()
   selected_signals = list()
   selected_signals.append(availible_signals[0])
   selected_signals.append(availible_signals[1])
   for package in con.real_time_readings(selected_signals, duration=10, interval=6000):
      signal_readings = package.get_data()
      for signal in signal_readings:
         for data_value in signal.data:
            value = (data_value * signal.factor) + signal.offset


Scope protocol description
++++++++++++++++++++++++++
For all scope functions it is necessary to log in as user ``SCOPE``.
On controls with TNC640 the login password is sent encrypted. It is therefore not possible to use the scope functions.

The available channels on the control can be read by sending R_OC. Each package contains one or more signal descriptions.

General sequence of setting up and starting real time recording of data:
1. select reading interval and signals with R_OP
2. set trigger and interval (again?) with R_OD
3. repeatedly read new data with T_OK until no more data is received


How to set up two capture serial traffic with Wireshark
-------------------------------------------------------
To analyse the RS232 communication, two VMs where used.
- one Windows XP VM with TNCremo 
- one TNC320 VM

VirtualBox can simulate serial communication over a TCP connection. This makes capturing the data much easier than using a real RS232 connection.

To set up the connection, one VM has to be set up as the server and one as the client. It doesn't matter which one is the server, you only have to remember to start this VM first. The selection of the server also has implications for the captured traffic for the direction of the traffic.

Setup VM1 (TNC320)
++++++++++++++++++
- start VM to configure the serial connection
- enter machine parameters with key number ``123`` and set them up as follows:

  - Release of the RS-232-C/V.24 interface in the file manager: ``FALSE``
  - Data transfer rate in bauds: ``BAUD_57600`` (Default)
  - Communications protocol: ``BLOCKWISE`` (Default)
  - Data bits in each transferred character: ``8 Bits``
  - Type of parity checking: ``EVEN`` (Default)
  - Number of stop bits: ``1 Stop-Bit`` (Default)
  - Type of data-flow checking: ``NONE``
  - File system for file operation via serial interface: ``FE1`` (Default)
  - Block Check Character (BCC) is not a control character: ``FALSE`` (Default)
  - Status of the RTS line: ``FALSE`` (Default)
  - Define behavior after receipt of ETX: ``FALSE`` (Default)

- Enable Serial Port 1
- Select Port Mode ``TCP``
- leave ``connect to pipe/socket`` unchecked
- enter a port number eg. ``8000`` for path/address
This VM has to be started first, otherwise you get an error message

Setup VM2 (WinXP)
+++++++++++++++++
- Enable Serial Port 1
- Select Port Mode ``TCP``
- check ``connect to pipe/socket``
- enter ``localhost:8000`` for path/address

Capture data
++++++++++++
- Start VM1
- Start VM2
- Start Wireshark
- In Wireshark, set the filter to ``port 8000`` and start the capture
- Start TNCremo and select ``Serial connection LSV-2`` as connection type
- In the ``Settings`` tab, select COM1 and make sure that for tansmission speed ``automatic detection`` is selected
- Click ``Connect`` and start the communication with the control


::

   >....0x05
   <....0x10 0x30
   >....0x05
   <....0x10 0x30
   >....0x10 0x02
   >....0x41 0x5f 0x4c 0x47 0x49 0x4e 0x53 0x50 0x45 0x43 0x54 0x00 0x10 0x03 0x40 (A_LGINSPECT0x000x100x03@)
   <....0x10 0x31
   >....0x04
   <....0x05
   >....0x10 0x30
   <....0x10 0x02 0x54 0x5f 0x4f 0x4b 0x10 0x03 (0x100x02T_OK0x100x03) 
   <....0x0c
   >....0x10 0x31
   <....0x04
   >....0x05
   <....0x10 0x30
   >....0x10 0x02
   >....0x52 0x5f 0x56 0x52 0x10 0x03 0x0a (R_VR0x100x030x01)
   <....0x10 31
   >....0x04
   <....0x05
   >....0x10 0x30
   <....0x10 0x02 0x53 0x5f 0x56 0x52 0x54 0x4e (..S_VRTN= 
   <....0x43 0x33 0x32 0x30 0x00 0x37 0x37 0x31 0x38 0x35 0x35 0x20 0x31 0x38 0x20 0x53 (C320.771 855 18 S)
        0x50 0x31 0x00 0x42 0x61 0x73 0x69 0x63 0x20 0x56 0x31 0x38 0x2d 0x30 0x30 0x00 (P1.Basic  V18-00.)
        0x4e 0x6f 0x20 0x76 0x65 0x72 0x73 0x69 0x6f 0x6e 0x20 0x67 0x69 0x76 0x65 0x6e (No versi on given)
        0x00 0x30 0x30 0x30 0x30 0x30 0x30 0x30 0x31 0x30 0x30 0x30 0x30 0x30 0x31 0x30 (.0000000 10000010)
        0x30 0x00 0x10 0x03 0x71 (0...q)
   >....0x10 0x31
   <....0x04
   >....0x05
   <....0x10 0x30
   >....0x10 0x02
   >....0x52 0x5f 0x50 0x52 0x10 0x03 0x0c (R_PR...)
   <....0x10
   <....0x31
   >....0x04
   <....0x05




Findings for serial communication
---------------------------------
Each telegram is enclosed in one or more control characters. Besides signaling the start an end of a telegram, they also indicate the state or intention of the sender.

Compared to the Ethernet communication, LSV-2 over serial does not indicate the length of the telegram. Instead, controlcharacters are used to indicate the end of a telegram.

BCC check sum character
+++++++++++++++++++++++
In addition to the control characters, each telegram is also protected by a checksum. The checksum is calculated over the payload of the telegram by XORing all bytes of the payload and is sent as the last byte of the telegram.

The implementation of the BCC calculation was taken from the [Sistema-Flexivel-Heidenhain](https://github.com/pcosta18/Sistema-Flexivel-Heidenhain-) by pcosta18.

