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
- manusolve
- NeeXoo
- Baptou88

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
| iTNC530     | 340494 08 SP2  |
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

Take a look at [protocol.rst](https://github.com/drunsinn/pyLSV2/blob/master/docs/package.rst) for a more in depth explanation on the details of LSV2.

## Usage
See [lsv2_demo.py](https://github.com/drunsinn/pyLSV2/blob/master/scripts/lsv2_demo.py) for a demonstration of some of the functions.

### Notes for upgrade to v1.xx
Notice: The change from 0.xx to 1.xx brought some major incompatible changes in regards to the API:
 - raise the minimal required python version to 3.5, future releases (1.1.x) will target 3.7 or higher
 - change of function names and parameters to better reflect their use
 - change of return types from dict to data classes to reduce the dependency on magic strings
These changes where made intentionally to make further development easier. See the demo script for an overview of the new API.

#### exemplary overview of the changes from v0.x to v1.x
| Functionality                | Version 0.x                                         | Version 1.x                                       |
|------------------------------|-----------------------------------------------------|---------------------------------------------------|
| read nc software version     | con.get_versions()["NC_Version"]                    | con.versions.nc_sw                                |
| check if control is a iTNC   | con.is_itnc()                                       | con.version.is_itnc()                             |
| get execution status via     | con.get_execution_status() returns plain int value  | con.execution_status() returns enum ExecState     |
| read override values via     | con.get_override_info() returns dict or False       | con.override_info() returns OverrideState or None |
| read axes position via       | con.get_axes_location() returns dict or False       | con.axes_location() returns dict or None          |
| move a file on the control   | con.move_local_file()                               | con.move_file()                                   |

### Basic example without context manager
```
 import pyLSV2
 con = pyLSV2.LSV2("192.168.56.101")
 con.connect()
 print(con.versions.control)
 con.disconnect()
```

### Basic example with context manager
```
 import pyLSV2
 with pyLSV2.LSV2("192.168.56.101") as con:
 ... con.connect()
 ... print(con.versions.control)
```

### Accessing PLC data
 To read values from the PLC memory you need to know the memory area/type and the memory address. There are two ways to read these values.
 
#### Reading via memory address
 The following command reads 15 marker (bits) starting at address 32. This returns a list with 15 boolean values.

```
 con.read_plc_memory(32, pyLSV2.MemoryType.MARKER, 15)
```
 See [lsv2_demo.py](https://github.com/drunsinn/pyLSV2/blob/master/scripts/lsv2_demo.py) for more examples.

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
 
 See [lsv2_demo.py](https://github.com/drunsinn/pyLSV2/blob/master/scripts/lsv2_demo.py) for more examples.

### SSH Tunnel
Newer controls allow the use of ssh to encrypt the communication via LSV2. See [ssh_tunnel_demo.py](https://github.com/drunsinn/pyLSV2/blob/master/scripts/ssh_tunnel_demo.py) for an example on how to use the python library [sshtunnel](https://github.com/pahaz/sshtunnel) to achieve a secure connection.

# Tables
 Included in this library is also functionality to work with Tables used by different NC Controls. This includes for example TNC controls as well as Anilam 6000i CNC. As these controls and there software versions use different table formats, it is also possible to dreive the format form an existing table and export the format to a json file.

 See [tyb2csv.py](https://github.com/drunsinn/pyLSV2/blob/master/scripts/tab2csv.py) for a demonstration on how to read a table and convert it to a csv file.

 This script can also be used as a command line tool
```
 usage: tab2csv.py [-h] [--decimal_char DECIMAL_CHAR] [-d | -v] source
 
 command line script parsing table files
 
 positional arguments:
   source                table file to parse
 
 options:
   -h, --help            show this help message and exit
   --decimal_char DECIMAL_CHAR
                         override local decimal char
   -d, --debug           enable log level DEBUG
   -v, --verbose         enable log level INFO
```

# Testing
 To run the test you either need a machine or a programming station. The control has to be on and the 
 PLC program has to be running. The IP address and timeout are set via command line parameters.
```
 pytest --address=192.168.56.103 --timeout=5
```

# determine minimum required python version
 The minimum required python version was checked with [vermin](https://github.com/netromdk/vermin).
```
 vermin --no-parse-comments .
```
The results indicate that pyLSV2 should work with python 3.5 and even with 3.4 if you install the packported modules argparse, enum and typing. While argpares is only used in the demo script the other two are necessary. Therefore it should be possible to use pyLSV2 with the curretn version of [IronPython](https://ironpython.net/) if you install these two modules.

# Resources
 - https://www.inventcom.net/support/heidenhain/read-tnc-plc-data
 - https://www.inventcom.net/s1/_pdf/Heidenhain_TNC_Machine_Data.pdf
 - https://www.yumpu.com/de/document/read/18882603/-f-heidenhain
 - https://de.industryarena.com/heidenhain/forum
 - https://github.com/drunsinn/pyLSV2/files/10254868/SDK_Help.zip