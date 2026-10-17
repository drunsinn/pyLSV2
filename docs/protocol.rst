Findings on LSV2
================
This document is a collection of information discovered while developing
this library.

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

These entries are observations, not guarantees for every control or NC
software version. In particular, on a TNC 640 with NC software
340590 10 SP2, an ``R_RI`` scan found selectors 20–26, but selectors 27,
28, and 51 returned ``T_ER_UNKNOWN_TELE`` even with DNC or DIAGNOSTICS
access. Selectors 20 and 21 returned data, but their layouts are not fully
known and must not be decoded like selector 22 (axis locations). Selector
24 could return the selected program without DNC, but its block number was
zero; DNC access was needed for the current block number. Selectors 25 and
26 required DNC access on that control.

The iTNC 530 lifetime timer selectors 30–34 have been observed on
iTNC 530 software versions 340490 02/04 and 606421 01. They return
big-endian 32-bit seconds representing lifetime counters, not the runtime
of the current program. These selectors returned ``T_ER_UNKNOWN_TELE`` on
the TNC 640 software version above. Selector availability and access
requirements therefore depend on the control generation and NC software.

On a TNC 640 VM with NC software 340595 18 SP4, selectors 20 and 21 were
readable with INSPECT access. Selector 20 returned a 16-bit count, two
arrays of 16-bit values, and that many null-terminated axis names. The
meaning of the second numeric array is not yet known. Selector 21 returned
a 16-bit count, that many 16-bit axis IDs, then two arrays of
null-terminated strings: values and physical axis names. The meaning of
the value strings is also unknown, so the decoders preserve them as text.

Information on the protocol based on reverse engineering and prior work
-----------------------------------------------------------------------
Each LSV2 telegram starts with a 32 bit length value followed by a command
string consisting of exactly 4 characters. The length value does not include
the command string, a telegram with only a command and no additional data
will have a length value of 0x0000.
If additional data has to be sent after the command string the value 0x00
is used as a separator.
All values are transmitted with big-endian byte order.

Log buffer
----------
Although ``R_LB`` is listed in the Toolbox command reference as the request
for a log buffer, it returned ``T_ER_UNKNOWN_TELE`` on the tested iTNC 530
and TNC 640 controls, including when DIAGNOSTICS access was granted. The
Toolbox sequence ``C_ST`` → ``M_LB`` → ``R_LB`` was not usable on those
controls, so ``R_LB`` should not be assumed to provide an event journal.
This is an observation on the tested controls and does not establish
support on other generations or software versions.

File Info
---------
By using the command ``R_FI`` followed by a valid file path, the control
responds with information about the file. This includes its size, Unix date,
and filename.
The message also contains additional bytes whose purpose is not yet
confirmed. These are probably attributes and/or access rights.

Directory info
--------------
The command for reading a directory seems to support an additional
parameter. With 0x01 sent after the command, the control sends all entries
at once instead of one entry per packet. ``R_DI`` 0x01 requests all
information at once.

The directory information has not been completely decoded. It contains the
full folder path and many zero bytes. Comparing results from different
controls and directories suggests a list of four-byte keys, but their
purpose is not yet known.
The first 4 bytes might be related to the size, but are always reported as
0xFF FF FF FF, which would decode to 4.2 Gbyte. They might instead indicate
the remaining free disk space.

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

DNC login is only possible if the option is set on the control. Without the
option, the control returns an error when attempting a DNC login.

Creating a log file - not implemented
-------------------------------------
The following sequence was captured with Wireshark while communicating
between the control and TNCremo.

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

To trigger log file generation, the ``C_CC`` telegram with command 27 is
used. Its parameters contain the log filename and the start date and time
for the log entries.
The control acknowledges this with ``T_OK``. After some time, another
telegram is received: ``M_CC`` with data 0x00 1b 00 64. This seems to signal
that the log file was created successfully and is ready to be copied.
Afterwards a regular file copy takes place.

File transfer
-------------
Files can be transferred in binary or ASCII mode. To enable binary mode,
add 0x01 after the filename. TNCremo lists file types for which binary mode
is recommended.
The functions :py:meth:`pyLSV2.LSV2.recive_file` and
:py:meth:`pyLSV2.LSV2.send_file` can be configured with the
``binary_mode`` parameter.

Scope
-----
LSV2 also includes functions to record live data in a style similar to an
oscilloscope. The OEM software is called TNCscope.
Traffic analysis made it possible to implement a subset of the protocol
needed to emulate TNCscope. More modern controls seem to require special
encryption, so pyLSV2 only supports the scope functions for iTNC controls.
To read data, first read the available signals from the control and select
the ones of interest. Each signal type has a different interval value,
which is the minimum time step between readings.
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
On TNC 640 controls, the login password is sent encrypted. It is therefore
not possible to use the scope functions.

The available channels on the control can be read by sending ``R_OC``.
Each package contains one or more signal descriptions.

General sequence of setting up and starting real time recording of data:
1. select reading interval and signals with R_OP
2. set trigger and interval (again?) with R_OD
3. repeatedly read new data with T_OK until no more data is received
