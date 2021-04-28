# pyLSV2
 This library is an attempt to implement the LSV2 communication protocol used by certain CNC controls. It's goal is to transfer file between the application and the control as well as collect information about the control files.
 Most of this library is based on the work of tfischer73 and his Eclipse plugin found at https://github.com/tfischer73/Eclipse-Plugin-Heidenhain . Since there is no free  documentation beside the plugin, some parts are based purely on reverse engineering and might therefore be not correct.
 Please consider the dangers of using this library on a production machine! This library is by no means complete and could damage the control or cause injuries! Everything beyond simple file manipulation is blocked by a lockout parameter. Use at your own risk!

## License
 MIT License

 Copyright (c) 2020 - 2021 drunsinn

 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.

## News and Releases
check [the github release page](https://github.com/drunsinn/pyLSV2/releases) for information on the latest updates

## Contributors
tfischer73
drunsinn
WouterElfrink
kekec14
Michal Navrátil

## Compatibility
Since there are a lot of different software versions and machine configurations out there 
it is hard to say if this library is compatible with all of them. Most testing has been done 
on programming stations but also with real hardware. Here is a list of versions have been tested:

### Programming Stations
| Control     | Software       |
|-------------|----------------|
| TNC640      | 340595 08 SP1  |
| TNC640      | 340595 10 SP2  |
| iTNC530     | 606425 04 SP20 |
| CNCpilot640 | 1230521 03 SP1 |

### Machines
| Control     | Software       |
|-------------|----------------|
| TNC640      | 340595 08 SP1  |
| iTNC530     | 340480 14 SP4  |
| iTNC530     | 606420 02 SP14 |

If you have tested it on one of your machines with a different software version, please let us know!

## Usage
Notice that the definitionns of constant values will be moved from pyLSV2.LSV2 to pyLSV2 directly!

### Basic example
```
 import pyLSV2
 con = pyLSV2.LSV2('192.168.56.101')
 con.connect()
 print(con.get_versions())
 con.disconnect()
```

### Reading Information from the control
```
 import logging
 import pyLSV2
 
 logging.basicConfig(level=logging.DEBUG)
 con = pyLSV2.LSV2('192.168.56.101', safe_mode=False)
 con.connect()
 print(con.get_program_status_text(con.get_program_status()))
 print(con.get_execution_status_text(con.get_execution_status()))
 con.disconnect()
```

### Accessing PLC data 
see scripts/lsv2_demo.py

## Information on the protocol based on reverse engineering and prior work
 Each LSV2 telegram starts with a 32 bit length value followed by a command string consisting of exactly 4 characters. The length value does not include the command string, a telegram with only a command and no additional data will have a length value of 0x0000.
 If additional data has to be sent after the command string the value 0x00 is used as a separator.
 All values are transmitted with big-endian byte order.

### File Info
 By using the command R_FI followed by a valid file path, the control responds with information about this file. This includes the file size, the unix-date and the filename.
 The message also contains some additional bytes which purpose is not yet confirmed. These bytes are probably attributes and/or access rights.

### Directory info
 The command for reading the content of a directory seems to support an additional parameter. With 0x01 sent after the command, the control sends all entries at once and not one entry per packet.
 R_DI 0x01 -> all info at once and not in separate packets

 The directory information has also not been completely decoded yet. It contains the full path of the folder and a lot of zero bytes. By comparing results from different controls and directories it was determined that there seem to be a list of four byte-keys. their purpose is not yet known.
 The first 4 bytes might have something to do with the size but it is always reported as 0xFF FF FF FF which would decode to 4,2 Gbyte. It might also be an indicator of the remaining free size of the disk.

### Machine State
 Base on discussion from github.com https://github.com/tfischer73/Eclipse-Plugin-Heidenhain/issues/1

 Login with INSPECT
```
   > R_RI 0x0015 (21) -> you can read the X,Y,Z Axis.
```

 Login with DNC
```
   > R_RI 0x0018 (24) -> you can read the name of the current program in execution.
```

 Login with DNC
```
   > R_RI 0x001A (26) -> you can read the current program status
```
   The states of program can be:
   0: Started
   1: Stopped
   2: Finished
   3: Cancelled
   4: Interrupted
   5: Error
   6: Error Cleared
   7: Idle
   8: Undefined

DNC login is only possible if the option is set on the control, without the option you get an error when trying to login with DNC.

### Creating a log file - not implemented
 By recording the communiction with Wireshark between the control and TNCremo the following sequence was accired.

```
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
```

 To trigger the generation of the log file, the telegram C_CC with command 27 is used. The parameters contain the filename of the log file an the start-date and time for the log entries.
 This is to acknowledge with a T_OK. After some time another telegram is receive: M_CC with data 0x00 1b 00 64. This seems to be the signal that the log file was created successfully and is ready to be copied.
 Afterwards a regular file copy takes place.

### File transfer
 Transfer of files can happen in binary or ASCII mode. To enable binary mode, add 0x01 after the filename. In TNCremo you can find a list of file types for which binary mode is recommended.
 The functions recive_file and send_file can be configured with the parameter binary_mode.

# Testing
To run the test you either need a machine or a programming station. The controls has to be on and the 
PLC program has to be running. You can add the IP-Address and timeout as a parameter
```
pytest --address=192.168.56.103 --timeout=0.1
```

# Resources
https://www.inventcom.net/support/heidenhain/read-tnc-plc-data

https://de.industryarena.com/heidenhain/forum
