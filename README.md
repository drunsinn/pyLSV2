# pyLSV2

[![PyPI pyversions](https://img.shields.io/pypi/pyversions/pyLSV2.svg)](https://pypi.python.org/pypi/pyLSV2/)
[![PyPI version fury.io](https://badge.fury.io/py/pyLSV2.svg)](https://pypi.python.org/pypi/pyLSV2/)
[![Documentation Status](https://readthedocs.org/projects/pylsv2/badge/?version=latest)](https://pylsv2.readthedocs.io/en/latest/?badge=latest)


 This library is an attempt to implement the LSV2 communication protocol used by certain
 CNC controls. It's main goal is to transfer file between the application and the control as well
 as collect information about said files. Over time more and more functions where added which
 support gathering information from the control.

 Most of this library is based on the work of tfischer73 and his Eclipse plugin found at [his GitHub page](https://github.com/tfischer73/Eclipse-Plugin-Heidenhain). Since there is no free  documentation beside the plugin, some parts are based purely on reverse engineering and might therefore be not correct.

 As long as no encrypted communication is necessary, no additional librarys are necessary.
 
 Please consider the dangers of using this library on a production machine! This library is by no means complete and could damage the control or cause injuries! Everything beyond simple file manipulation is blocked by a lockout parameter. Use at your own risk!

## License
 MIT License

 Copyright (c) 2020 - 2022 drunsinn

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
In chronological order:
- tfischer73
- drunsinn
- WouterElfrink
- kekec14
- Michal Navrátil
- PandaRoux8
- sazima

## Compatibility
Since there are a lot of different software versions and machine configurations out there 
it is hard to say if this library is compatible with all of them. Most testing has been done 
on programming stations but also with real hardware. Here is a list of versions that have
been tested:

### Programming Stations
| Control     | Software       |
|-------------|----------------|
| TNC640      | 340595 08 SP1  |
| TNC640      | 340595 10 SP2  |
| TNC640      | 340595 11 SP1  |
| TNC640      | 340595 11 SP4  |
| iTNC530     | 606425 04 SP20 |
| CNCpilot640 | 1230521 03 SP1 |

### Machines
| Control     | Software       |
|-------------|----------------|
| TNC620      | 817605 04 SP1  |
| TNC640      | 340595 08 SP1  |
| iTNC530     | 340480 14 SP4  |
| iTNC530     | 606420 02 SP14 |
| iTNC530     | 606420 02 SP3  |

If you have tested it on one of your machines with a different software version, please let us know!

Take a look at [protocol.rst](https://github.com/drunsinn/pyLSV2/blob/c0631b7cfbe033ce2727ea07fe5202e967e086c9/docs/protocol.rst) for a more in depth explanation on the detials of LSV2.

## Usage
See [lsv2_demo.py](https://github.com/drunsinn/pyLSV2/blob/c85d1dc64ce7c5f7e2941d0f558a22a6c702798f/scripts/lsv2_demo.py) for a demonstration of some of the functions.

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
 print(con.get_axes_location())
 con.disconnect()
```

### File transfer
```
 import logging
 import pyLSV2
 
 logging.basicConfig(level=logging.DEBUG)
 con = pyLSV2.LSV2('192.168.56.101', safe_mode=True)
 con.connect()

 con.send_file(local_path='./test.H', remote_path='TNC:/',
               override_file=True, binary_mode=True)

 con.recive_file(local_path='./', remote_path='TNC:/nc_prog/$mdi.h',
                 override_file=True, binary_mode=True)

 con.disconnect()
```

### Accessing PLC data
 To read values from the PLC memory you need to know the memory area/type and the memory address. There are two ways to read these values.
 
#### Reading via memory address
 The following command reads 15 marker (bits) starting at address

```
 con.read_plc_memory(address=32, mem_type=pyLSV2.PLC_MEM_TYPE_MARKER, count=15)
```
 See [lsv2_demo.py](https://github.com/drunsinn/pyLSV2/blob/c85d1dc64ce7c5f7e2941d0f558a22a6c702798f/scripts/lsv2_demo.py) for more examples.

 The available memory aread and their python data type
| Memory Type              | Python Type |
|--------------------------|-------------|
| PLC_MEM_TYPE_MARKER      | bool        |
| PLC_MEM_TYPE_INPUT       | bool        |
| PLC_MEM_TYPE_OUTPUT      | bool        |
| PLC_MEM_TYPE_COUNTER     | bool        |
| PLC_MEM_TYPE_TIMER       | bool        |
| PLC_MEM_TYPE_BYTE        | integer     |
| PLC_MEM_TYPE_WORD        | integer     |
| PLC_MEM_TYPE_DWORD       | integer     |
| PLC_MEM_TYPE_STRING      | str         |
| PLC_MEM_TYPE_INPUT_WORD  | integer     |
| PLC_MEM_TYPE_OUTPUT_WORD | integer     |

#### Reading via Data Path
 The following command reads values from the control not via a memory address but via supplying a data access path. This will only work on iTNC controls!
 The advantage is that it also allows you to access tables like the tool table without reading the complete file.

```
 con.read_data_path('/PLC/memory/K/1')
 con.read_data_path('/TABLE/TOOL/T/1/DOC')
```
 
 See [lsv2_demo.py](https://github.com/drunsinn/pyLSV2/blob/c85d1dc64ce7c5f7e2941d0f558a22a6c702798f/scripts/lsv2_demo.py) for more examples.

### SSH Tunnel
Newer controls allow the use of ssh to encrypt the communication via LSV2. See scripts/ssh_tunnel_demo.py for an example on how to use the python library [sshtunnel](https://github.com/pahaz/sshtunnel) to achieve a secure connection.

# Tables
Included in this library is also fuctionality to work with Tables used by different NC Controls. This includes for example TNC controls as well as Anilam 6000i CNC. As these controls and there software versions use different table formats, it is also possible to dreive the format form an existing table and export the format to a json file.

 See [table_reader_demo.py](https://github.com/drunsinn/pyLSV2/blob/31b9d867c28bb34c7b9e0cfc80270d4277b2079a/scripts/table_reader_demo.py) for a demonstration on how to read a table and convert it to a different format.

# Testing
 To run the test you either need a machine or a programming station. The controls has to be on and the 
 PLC program has to be running. You can add the IP-Address and timeout as a parameter
```
 pytest --address=192.168.56.103 --timeout=5
```

# Resources
https://www.inventcom.net/support/heidenhain/read-tnc-plc-data

https://de.industryarena.com/heidenhain/forum
