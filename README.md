# pyLSV2
 This library is an attempt to implement the LSV2 communication protocol used by certain CNC controls. It's goal is to transfer file between the application and the control as well as collect information about the control files.
 Most of this library is based on the work of tfischer73 and his Eclipse plugin found at https://github.com/tfischer73/Eclipse-Plugin-Heidenhain . Since there is no free  documentation beside the plugin, some parts are based purely on reverse engineering and might therefore be not correct.
 Please consider the dangers of using this library on a production machine! This library is by no means complete and could damage the control or cause injuries! Everything beyond simple file manipulation is blocked by a lockout parameter. Use at your own risk!

## License
 MIT License

 Copyright (c) 2020 drunsinn

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

## Usage
 import pyLSV2
 con = pyLSV2.LSV2('192.168.56.101', port=19000)
 con.connect()
 print(con.get_versions())
 con.disconnect()

## Information on the protocol based on reverse engineering and prior work
 Each LSV2 telegram starts with a 32 bit length value followed by a command string consisting of exactly 4 characters. The length value does not include the command string, a telegram with only a command and no additional data will have a length value of 0x0000.
 If additional data has to be sent after the command string the value 0x00 is used as a separator.
 All values are transmitted with big-endian byte order.
