#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
data classes for pyLSV2

after migration to python 3.7+ these will be changed to @dataclass!
"""

from datetime import datetime
import struct
import re
from typing import List

from .const import ControlType, LSV2StatusCode, ChannelType
from .err import LSV2DataException


class VersionInfo:
    """data class for version information"""

    def __init__(self):
        """init with default values"""
        self.control = ""
        self.type = ControlType.UNKNOWN
        self.nc_sw = ""
        self.plc = ""
        self.splc = ""
        self.option_bits = ""
        self.id_number = ""
        self.release = ""

        self._ncsw_reg = re.compile(r"(?P<base>\d{5})(?P<type>\d)(?:[ -])(?P<version>\d+)(?: (?P<sp>.*))?")

    def __str__(self) -> str:
        return "%s / %s" % (self.control, self.nc_sw)

    @property
    def control(self) -> str:
        """
        version identifier of the control

        :getter: returns the version string
        :setter: sets the version string
        """
        return self._control_version

    @control.setter
    def control(self, value: str):
        value = value.replace(" ", "").strip()
        self._control_version = value

        value = value.upper()

        if value.startswith("ITNC530"):
            self.type = ControlType.MILL_OLD
        elif value.startswith("TNC640"):
            self.type = ControlType.MILL_NEW
        elif value.startswith("TNC620"):
            self.type = ControlType.MILL_NEW
        elif value.startswith("TNC320"):
            self.type = ControlType.MILL_NEW
        elif value.startswith("TNC128"):
            self.type = ControlType.MILL_NEW
        elif value.startswith("MANUALPLUS"):
            self.type = ControlType.LATHE_NEW
        elif value.startswith("CNCPILOT640"):
            self.type = ControlType.LATHE_NEW
        elif value.startswith("TNC7"):
            self.type = ControlType.TNC7
        elif value.startswith("MILLPLUS"):
            self.type = ControlType.MILLPLUS
        else:
            self.type = ControlType.UNKNOWN

    @property
    def type(self) -> ControlType:
        """
        control type identifier of the control

        :getter: returns the control type
        :setter: sets the control type
        """
        return self._control_type

    @type.setter
    def type(self, value: ControlType):
        self._control_type = value

    @property
    def nc_sw(self) -> str:
        """version identifier of the nc software"""
        return self._nc_version

    @nc_sw.setter
    def nc_sw(self, value: str):
        self._nc_version = value

    @property
    def plc(self) -> str:
        """version identifier of the plc software"""
        return self._plc_version

    @plc.setter
    def plc(self, value: str):
        self._plc_version = value

    @property
    def splc(self) -> str:
        """version identifier of the splc software"""
        return self._splc_version

    @splc.setter
    def splc(self, value: str):
        self._splc_version = value

    @property
    def option_bits(self) -> str:
        """available options in the control"""
        return self._option_bits

    @option_bits.setter
    def option_bits(self, value: str):
        self._option_bits = value

    @property
    def id_number(self) -> str:
        """id of the control"""
        return self._id_number

    @id_number.setter
    def id_number(self, value: str):
        self._id_number = value

    @property
    def release(self) -> str:
        """release type ???"""
        return self._release_type

    @release.setter
    def release(self, value: str):
        self._release_type = value

    def is_itnc(self) -> bool:
        """return ``True`` if control is a iTNC"""
        return self._control_type == ControlType.MILL_OLD

    def is_tnc(self) -> bool:
        """return ``True`` if control is a TNC"""
        return self._control_type == ControlType.MILL_NEW

    def is_pilot(self) -> bool:
        """return ``True`` if control is a CNCPILOT640"""
        return self._control_type == ControlType.LATHE_NEW

    def is_manualplus(self) -> bool:
        """return ``True`` if control is a MANUALplus620"""
        return self._control_type == ControlType.LATHE_NEW

    def is_millplus(self) -> bool:
        """return ``True`` if control is a MillPlus"""
        return self._control_type == ControlType.MILLPLUS

    def is_tnc7(self) -> bool:
        """return ```True``` if control is a TNC7"""
        return self._control_type == ControlType.TNC7

    @property
    def nc_sw_base(self) -> int:
        """base nc software as integer"""
        result = self._ncsw_reg.fullmatch(self.nc_sw)
        if result is None or "base" not in result.groupdict():
            raise LSV2DataException("could not parse nc software base version from '%s'" % self.nc_sw)
        return int(result.group("base")) * 10

    @property
    def nc_sw_type(self) -> int:
        """nc software type"""
        result = self._ncsw_reg.fullmatch(self.nc_sw)
        if result is None or "type" not in result.groupdict():
            raise LSV2DataException("could not parse nc software type from '%s'" % self.nc_sw)
        return int(result.group("type"))

    @property
    def nc_sw_version(self) -> int:
        """nc software version number"""
        result = self._ncsw_reg.fullmatch(self.nc_sw)
        if result is None or "version" not in result.groupdict():
            raise LSV2DataException("could not parse nc software version from '%s'" % self.nc_sw)
        return int(result.group("version"))

    @property
    def nc_sw_service_pack(self) -> int:
        """service pack number"""
        result = self._ncsw_reg.fullmatch(self.nc_sw)
        if result is None:
            raise LSV2DataException("could not parse service pack from '%s'" % self.nc_sw)
        if result.group("sp") is None:
            return 0
        sp_str = result.group("sp").lower()
        sp_str = sp_str.lstrip("sp")
        return int(sp_str)


class SystemParameters:
    """data class for system parameters"""

    def __init__(self):
        """init with default values"""
        self.inputs_start_address = -1
        self.number_of_inputs = -1
        self.outputs_start_address = -1
        self.number_of_outputs = -1

        self.counters_start_address = -1
        self.number_of_counters = -1

        self.timers_start_address = -1
        self.number_of_timers = -1

        self.words_start_address = -1
        self.number_of_words = -1

        self.strings_start_address = -1
        self.number_of_strings = -1
        self.max_string_lenght = -1

        self.input_words_start_address = -1
        self.number_of_input_words = -1

        self.output_words_start_address = -1
        self.number_of_output_words = -1

        self.lsv2_version = -1
        self.lsv2_version_flags = -1
        self.sv2_version_flags_ex = -1

        self.max_block_length = -1

        self.bin_version = -1
        self.bin_revision = -1
        self.iso_version = -1
        self.iso_revision = -1

        self.hardware_version = -1

        self.max_trace_line = -1
        self.number_of_scope_channels = -1

        self.password_encryption_key = -1

        self.turbo_mode_active = False
        self.dnc_mode_allowed = False
        self.axes_sampling_rate = -1

    @property
    def markers_start_address(self) -> int:
        """memory start address for markers"""
        return self._markers_start_address

    @markers_start_address.setter
    def markers_start_address(self, value: int):
        self._markers_start_address = value

    @property
    def number_of_markers(self) -> int:
        """total number of markers"""
        return self._number_of_markers

    @number_of_markers.setter
    def number_of_markers(self, value: int):
        self._number_of_markers = value

    @property
    def inputs_start_address(self) -> int:
        """memory start address for inputs"""
        return self._inputs_start_address

    @inputs_start_address.setter
    def inputs_start_address(self, value: int):
        self._inputs_start_address = value

    @property
    def number_of_inputs(self) -> int:
        """total number of inputs"""
        return self._number_of_inputs

    @number_of_inputs.setter
    def number_of_inputs(self, value: int):
        self._number_of_inputs = value

    @property
    def outputs_start_address(self) -> int:
        """memory start address for outputs"""
        return self._outputs_start_address

    @outputs_start_address.setter
    def outputs_start_address(self, value: int):
        self._outputs_start_address = value

    @property
    def number_of_outputs(self) -> int:
        """total number of outputs"""
        return self._number_of_outputs

    @number_of_outputs.setter
    def number_of_outputs(self, value: int):
        self._number_of_outputs = value

    @property
    def counters_start_address(self) -> int:
        """memory start address for counters"""
        return self._counters_start_address

    @counters_start_address.setter
    def counters_start_address(self, value: int):
        self._counters_start_address = value

    @property
    def number_of_counters(self) -> int:
        """total number of counters"""
        return self._number_of_counters

    @number_of_counters.setter
    def number_of_counters(self, value: int):
        self._number_of_counters = value

    @property
    def timers_start_address(self) -> int:
        """memory start address for timers"""
        return self._timers_start_address

    @timers_start_address.setter
    def timers_start_address(self, value: int):
        self._timers_start_address = value

    @property
    def number_of_timers(self) -> int:
        """total number of timers"""
        return self._number_of_timers

    @number_of_timers.setter
    def number_of_timers(self, value: int):
        self._number_of_timers = value

    @property
    def words_start_address(self) -> int:
        """memory start address for words"""
        return self._words_start_address

    @words_start_address.setter
    def words_start_address(self, value: int):
        self._words_start_address = value

    @property
    def number_of_words(self) -> int:
        """total number of words"""
        return self._number_of_words

    @number_of_words.setter
    def number_of_words(self, value: int):
        self._number_of_words = value

    @property
    def strings_start_address(self) -> int:
        """memory start address for strings"""
        return self._strings_start_address

    @strings_start_address.setter
    def strings_start_address(self, value: int):
        self._strings_start_address = value

    @property
    def number_of_strings(self) -> int:
        """total number of strings"""
        return self._number_of_strings

    @number_of_strings.setter
    def number_of_strings(self, value: int):
        self._number_of_strings = value

    @property
    def max_string_lenght(self) -> int:
        """maximum number of bytes in a string"""
        return self._max_string_lenght

    @max_string_lenght.setter
    def max_string_lenght(self, value: int):
        self._max_string_lenght = value

    @property
    def input_words_start_address(self) -> int:
        """memory start address for input words"""
        return self._input_words_start_address

    @input_words_start_address.setter
    def input_words_start_address(self, value: int):
        self._input_words_start_address = value

    @property
    def number_of_input_words(self) -> int:
        """total number of input words"""
        return self._number_of_input_words

    @number_of_input_words.setter
    def number_of_input_words(self, value: int):
        self._number_of_input_words = value

    @property
    def output_words_start_address(self) -> int:
        """memory start address for output words"""
        return self._output_words_start_address

    @output_words_start_address.setter
    def output_words_start_address(self, value: int):
        self._output_words_start_address = value

    @property
    def number_of_output_words(self) -> int:
        """total number of output words"""
        return self._number_of_output_words

    @number_of_output_words.setter
    def number_of_output_words(self, value: int):
        self._number_of_output_words = value

    @property
    def lsv2_version(self) -> int:
        """version of the LSV2 protocol used"""
        return self._lsv2_version

    @lsv2_version.setter
    def lsv2_version(self, value: int):
        self._lsv2_version = value

    @property
    def lsv2_version_flags(self) -> int:
        """feature flags used by this version of LSV2"""
        return self._lsv2_version_flags

    @lsv2_version_flags.setter
    def lsv2_version_flags(self, value: int):
        self._lsv2_version_flags = value

    @property
    def lsv2_version_flags_ex(self) -> int:
        """additional feature flags used by this version of LSV2"""
        return self._lsv2_version_flags_ex

    @lsv2_version_flags_ex.setter
    def lsv2_version_flags_ex(self, value: int):
        self._lsv2_version_flags_ex = value

    @property
    def max_block_length(self) -> int:
        """maximal number of bytes that can be sent and received by the control"""
        return self._max_block_length

    @max_block_length.setter
    def max_block_length(self, value: int):
        self._max_block_length = value

    @property
    def bin_version(self) -> int:
        """bin version ???"""
        return self._bin_version

    @bin_version.setter
    def bin_version(self, value: int):
        self._bin_version = value

    @property
    def bin_revision(self) -> int:
        """bin revisiion ???"""
        return self._bin_revision

    @bin_revision.setter
    def bin_revision(self, value: int):
        self._bin_revision = value

    @property
    def iso_version(self) -> int:
        """iso revisiion ???"""
        return self._iso_version

    @iso_version.setter
    def iso_version(self, value: int):
        self._iso_version = value

    @property
    def iso_revision(self) -> int:
        """iso revisiion ???"""
        return self._iso_revision

    @iso_revision.setter
    def iso_revision(self, value: int):
        self._iso_revision = value

    @property
    def hardware_version(self) -> int:
        """hardware revisiion ???"""
        return self._hardware_version

    @hardware_version.setter
    def hardware_version(self, value: int):
        self._hardware_version = value

    @property
    def max_trace_line(self) -> int:
        """maximum number of trace lines??"""
        return self._max_trace_line

    @max_trace_line.setter
    def max_trace_line(self, value: int):
        self._max_trace_line = value

    @property
    def number_of_scope_channels(self) -> int:
        """number of channels used by the scope"""
        return self._number_of_scope_channels

    @number_of_scope_channels.setter
    def number_of_scope_channels(self, value: int):
        self._number_of_scope_channels = value

    @property
    def password_encryption_key(self) -> int:
        """???"""
        return self._password_encryption_key

    @password_encryption_key.setter
    def password_encryption_key(self, value: int):
        self._password_encryption_key = value

    @property
    def turbo_mode_active(self) -> bool:
        """is turbo mode active?"""
        return self._turbo_mode_active

    @turbo_mode_active.setter
    def turbo_mode_active(self, value: bool):
        self._turbo_mode_active = value

    @property
    def dnc_mode_allowed(self) -> bool:
        """is dnc mode allowed?"""
        return self._dnc_mode_allowed

    @dnc_mode_allowed.setter
    def dnc_mode_allowed(self, value: bool):
        self._dnc_mode_allowed = value

    @property
    def axes_sampling_rate(self) -> int:
        """axes sampling rate"""
        return self._axes_sampling_rate

    @axes_sampling_rate.setter
    def axes_sampling_rate(self, value: int):
        self._axes_sampling_rate = value


class ToolInformation:
    """data class for information about a tool"""

    def __init__(self):
        """init with default values"""
        self.number = -1
        self.index = -1
        self.axis = ""
        self.length = -1
        self.radius = -1
        self.name = ""

    @property
    def number(self) -> int:
        """tool number"""
        return self._number

    @number.setter
    def number(self, value: int):
        self._number = value

    @property
    def index(self) -> int:
        """index number"""
        return self._index

    @index.setter
    def index(self, value: int):
        self._index = value

    @property
    def axis(self) -> str:
        """tool/spindle axis"""
        return self._axis

    @axis.setter
    def axis(self, value: str):
        self._axis = value

    @property
    def length(self) -> float:
        """tool length"""
        return self._length

    @length.setter
    def length(self, value: float):
        self._length = value

    @property
    def radius(self) -> float:
        """tool radius"""
        return self._radius

    @radius.setter
    def radius(self, value: float):
        self._radius = value

    @property
    def name(self) -> str:
        """tool name"""
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value


class OverrideState:
    """data class for the override states"""

    def __init__(self):
        """init with default values"""
        self.feed = -1.0
        self.rapid = -1.0
        self.spindle = -1.0

    def __str__(self) -> str:
        return "F:%3.1f%% FMAX:%3.1f%% S:%3.1f%%" % (
            self.feed,
            self.rapid,
            self.spindle,
        )

    @property
    def feed(self) -> float:
        """override value for feed rate"""
        return self._feed

    @feed.setter
    def feed(self, value: float):
        self._feed = value

    @property
    def rapid(self) -> float:
        """override value for rapid feed"""
        return self._rapid

    @rapid.setter
    def rapid(self, value: float):
        self._rapid = value

    @property
    def spindle(self) -> float:
        """override value for spindle speed"""
        return self._spindel

    @spindle.setter
    def spindle(self, value: float):
        self._spindel = value


class NCErrorMessage:
    """data class for nc error messages
    LSV2 error messages are handled with"""

    def __init__(self):
        """
        init with default values,
        names were chosen so not to interfere with existing names
        """
        self.e_class = -1
        self.e_group = -1
        self.e_number = -1
        self.e_text = ""
        self.dnc = False

    def __str__(self) -> str:
        return "Class: %d, Group: %d, Number: %d, DNC?: %s, Text: '%s'" % (
            self.e_class,
            self.e_group,
            self.e_number,
            self.dnc,
            self.e_text,
        )

    @property
    def e_class(self) -> int:
        """class of the error message"""
        return self._e_class

    @e_class.setter
    def e_class(self, value: int):
        self._e_class = value

    @property
    def e_group(self) -> int:
        """group of the error message"""
        return self._e_group

    @e_group.setter
    def e_group(self, value: int):
        self._e_group = value

    @property
    def e_number(self) -> int:
        """number of the error message"""
        return self._e_number

    @e_number.setter
    def e_number(self, value: int):
        self._e_number = value

    @property
    def e_text(self) -> str:
        """error message"""
        return self._e_text

    @e_text.setter
    def e_text(self, value: str):
        self._e_text = value

    @property
    def dnc(self) -> bool:
        """if True, message is related to DNC?"""
        return self._dnc

    @dnc.setter
    def dnc(self, value: bool):
        self._dnc = value


class StackState:
    """data class for the current execution stack"""

    def __init__(self):
        """init with default values"""
        self.line_no = -1
        self.main = ""
        self.current = ""

    def __str__(self) -> str:
        return "Main '%s' Current '%s' @ Line %d" % (
            self.main,
            self.current,
            self.line_no,
        )

    @property
    def line_no(self) -> int:
        """current line number being executed"""
        return self._current_line

    @line_no.setter
    def line_no(self, value: int):
        self._current_line = value

    @property
    def main(self) -> str:
        """name of the current main program"""
        return self._main_pgm

    @main.setter
    def main(self, value: str):
        self._main_pgm = value

    @property
    def current(self) -> str:
        """name of the current program being executed"""
        return self._current_pgm

    @current.setter
    def current(self, value: str):
        self._current_pgm = value


class FileEntry:
    """data class for file information"""

    def __init__(self):
        """init with default values"""
        self.size = -1
        self.timestamp = datetime.fromtimestamp(0)
        self.attributes = bytearray()

        self.is_changable = False
        self.is_drive = False
        self.is_directory = False
        self.is_protected = False
        self.is_hidden = False
        self.is_selected = False

        self.name = ""

    @property
    def size(self) -> int:
        """file size in bytes"""
        return self._size

    @size.setter
    def size(self, value: int):
        self._size = value

    @property
    def timestamp(self) -> datetime:
        """timestamp of last file change"""
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value: datetime):
        self._timestamp = value

    @property
    def attributes(self) -> bytearray:
        """byte array of file attributes"""
        return self._attributes

    @attributes.setter
    def attributes(self, value: bytearray):
        self._attributes = value

    @property
    def is_protected(self) -> bool:
        """if True, file is write protected"""
        return self._is_protected

    @is_protected.setter
    def is_protected(self, value: bool):
        self._is_protected = value

    @property
    def is_drive(self) -> bool:
        """if True, entry describes a drive"""
        return self._is_drive

    @is_drive.setter
    def is_drive(self, value: bool):
        self._is_drive = value

    @property
    def is_directory(self) -> bool:
        """if True, entry describes a directory"""
        return self._is_directory

    @is_directory.setter
    def is_directory(self, value: bool):
        self._is_directory = value

    @property
    def is_hidden(self) -> bool:
        """if True, object is hidden in file browser"""
        return self._is_hidden

    @is_hidden.setter
    def is_hidden(self, value: bool):
        self._is_hidden = value

    @property
    def is_selected(self) -> bool:
        """if True, object is selected for execution"""
        return self._is_selected

    @is_selected.setter
    def is_selected(self, value: bool):
        self._is_selected = value

    @property
    def name(self) -> str:
        """name of the file system object"""
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value


class DirectoryEntry:
    """data class for directory information"""

    def __init__(self):
        """init with default values"""
        self.free_size = -1
        self.dir_attributes = []
        self.attributes = bytearray()
        self.path = ""

    @property
    def free_size(self) -> int:
        """number of free bytes"""
        return self._free_size

    @free_size.setter
    def free_size(self, value: int):
        self._free_size = value

    @property
    def dir_attributes(self) -> List[str]:
        """attriutes of this directory"""
        return self._dir_attributes

    @dir_attributes.setter
    def dir_attributes(self, value: List[str]):
        self._dir_attributes = value

    @property
    def attributes(self) -> bytearray:
        """bytes of unknown data"""
        return self._attributes

    @attributes.setter
    def attributes(self, value: bytearray):
        self._attributes = value

    @property
    def path(self) -> str:
        """path of this directory"""
        return self._path

    @path.setter
    def path(self, value: str):
        self._path = value


class DriveEntry:
    """data class for drive information"""

    def __init__(self):
        """init with default values"""
        self.name = ""
        self.size = -1
        self.timestamp = datetime.fromtimestamp(0)
        self.attributes = bytearray()

    @property
    def name(self) -> str:
        """name of the drive"""
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def size(self) -> int:
        """file size in bytes"""
        return self._size

    @size.setter
    def size(self, value: int):
        self._size = value

    @property
    def timestamp(self) -> datetime:
        """timestamp of last file change"""
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value: datetime):
        self._timestamp = value

    @property
    def attributes(self) -> bytearray:
        """byte array of file attributes"""
        return self._attributes

    @attributes.setter
    def attributes(self, value: bytearray):
        self._attributes = value


class LSV2Error:
    """data class for LSV2 errors"""

    def __init__(self):
        """init with default values"""
        self.e_type = -1
        self.e_code = LSV2StatusCode.T_ER_NON

    def __str__(self):
        return "Error Type: %d, Error Code: %d" % (self.e_type, self.e_code)

    @property
    def e_type(self) -> int:
        """error type"""
        return self._error_type

    @e_type.setter
    def e_type(self, value: int):
        self._error_type = value

    @property
    def e_code(self) -> LSV2StatusCode:
        """error code"""
        return self._error_code

    @e_code.setter
    def e_code(self, value: LSV2StatusCode):
        self._error_code = value

    @staticmethod
    def from_ba(err_bytes: bytearray):
        """convert byte array to error object"""
        err = LSV2Error()
        err.e_type = struct.unpack("!BB", err_bytes)[0]
        err.e_code = struct.unpack("!BB", err_bytes)[1]
        return err


class ScopeSignal:
    def __init__(self):
        self._channel_name = ""
        self._channel = -1
        # self._channel_suffix = ""

        self._signale_name = ""
        self._signal = -1
        # self._signale_suffix = ""

        self._signal_type = ChannelType.UNKNOWN

        self._min_interval = -1
        # self._unknown = bytearray()

        self._signal_parameter = -1

        self._unit_string = ""

        self._offset = 0

        self._factor = 0.0

    def __str__(self):
        return "Channel/Signal: {:02d}/{:02d} '{:s} - {:s}' Type {:02d} Interval {:d}us Unit '{:s}' offset {:d} factor {:f} Optional Parameter {:d}".format(
            self.channel,
            self.signal,
            self.channel_name,
            self.signal_name,
            self.channel_type,
            self.min_interval,
            self.unit,
            self.offset,
            self.factor,
            self.signal_parameter,
        )

    @property
    def channel_name(self) -> str:
        """name of the scope channel"""
        return self._channel_name

    @channel_name.setter
    def channel_name(self, value: str):
        self._channel_name = value

    @property
    def signal_name(self) -> str:
        """name of the signal"""
        return self._signale_name

    @signal_name.setter
    def signal_name(self, value: str):
        self._signale_name = value

    @property
    def channel(self) -> int:
        """number of channel"""
        return self._channel

    @channel.setter
    def channel(self, value: int):
        self._channel = value

    @property
    def signal(self) -> int:
        """number of signal"""
        return self._signal

    @signal.setter
    def signal(self, value: int):
        self._signal = value

    @property
    def channel_type(self) -> ChannelType:
        """type of channel"""
        return self._channel_type

    @channel_type.setter
    def channel_type(self, value: ChannelType):
        self._channel_type = value

    # @property
    # def signal_suffix(self) -> str:
    #    """name suffix of the scope signal"""
    #    return self._signal_suffix

    # @signal_suffix.setter
    # def signal_suffix(self, value:str):
    #    self._signal_suffix = value

    @property
    def min_interval(self) -> int:
        """minimum signal interval in us"""
        return self._min_interval

    @min_interval.setter
    def min_interval(self, value: int):
        self._min_interval = value

    @property
    def signal_parameter(self) -> int:
        """parameter necessary to read signal"""
        return self._signal_parameter

    @signal_parameter.setter
    def signal_parameter(self, value: int):
        self._signal_parameter = value

    def needs_parameter(self) -> bool:
        """check if signal need an additional parameter"""
        if self.channel_type in [ChannelType.TYPE2, ChannelType.TYPE5]:
            return True
        return False

    @property
    def unit(self) -> str:
        """unit of the value"""
        return self._unit_string

    @unit.setter
    def unit(self, value: str):
        self._unit_string = value

    @property
    def offset(self) -> int:
        """signal offset"""
        return self._offset

    @offset.setter
    def offset(self, value: int):
        self._offset = value

    @property
    def factor(self) -> float:
        """signal scaling factor"""
        return self._factor

    @factor.setter
    def factor(self, value: float):
        self._factor = value

    # @property
    # def unknown(self) -> bytearray:
    #    """dict of values where it's unsure if the are correct"""
    #    return self._unknown

    # @unknown.setter
    # def unknown(self, value:bytearray):
    #    self._unknown = value

    def to_ba(self) -> bytearray:
        """create byte array necessary for enabling signal on control"""
        signal_data = bytearray()
        signal_data.extend(struct.pack("!H", self.channel))  # <- channel number
        if self.channel_type in [ChannelType.TYPE1, ChannelType.TYPE4]:
            signal_data.extend(struct.pack("!H", self.signal))  # <- signal number
            signal_data.extend(bytearray(b"\xff\xff\xff\xff"))  # <- ??
        elif self.channel_type in [ChannelType.TYPE2, ChannelType.TYPE5]:
            signal_data.extend(
                struct.pack("!H", self.signal)
            )  # <- PLC memory type: 0=M, 1=T, 2=C, 3=I, 4=O, 5=B, 6=W, 7=D, 8=IB, 9=IW, 10=ID, 11=OB, 12=OW, 12=OD
            signal_data.extend(struct.pack("!L", self.signal_parameter))
        else:
            signal_data.extend(bytearray(b"\xff\xff\xff\xff\xff\xff"))  # <- ??
        return signal_data

    def normalized_name(self) -> str:
        """combine signal and channel name into a normalised form"""
        c_name = self.channel_name.lower()
        c_name = c_name.replace(" ", "_")
        c_name = c_name.replace(".", "_")
        c_name = c_name.replace(":", "_")
        c_name = c_name.replace("(", "_")
        c_name = c_name.replace(")", "")
        c_name = c_name.replace("-", "_")
        c_name = c_name.replace("__", "_")
        c_name = c_name.strip("_")

        s_name = self.signal_name.lower().strip()

        if len(s_name) > 0:
            return s_name + "_" + c_name
        return c_name


class ScopeSignalData:
    def __init__(self, channel: int, signal: int, offset: int, factor: float, unit: str):
        self._channel = channel
        self._signal = signal
        self._offset = offset
        self._factor = factor
        self._unit = unit

        # self._header = bytearray()
        self.data: List[float] = []

    @property
    def channel(self) -> int:
        """number of channel"""
        return self._channel

    @property
    def signal(self) -> int:
        """number of signal"""
        return self._signal

    @property
    def offset(self) -> int:
        """data offset"""
        return self._offset

    @property
    def factor(self) -> float:
        """data factor"""
        return self._factor

    @property
    def unit(self) -> str:
        """data unit"""
        return self._unit

    # @property
    # def header(self) -> bytearray:
    #    """signal header"""
    #    return self._header

    # @header.setter
    # def header(self, value:bytearray):
    #    self._header = value


class ScopeReading:
    def __init__(self, sequence_number: int):
        self._seqence_nr = sequence_number
        # self._full_data = bytearray()
        self._signal_data: List[ScopeSignalData] = []

    def seqence_nr(self) -> int:
        """sequence number of consecuetive readings"""
        return self._seqence_nr

    def add_dataset(self, signal_data: ScopeSignalData):
        self._signal_data.append(signal_data)

    def get_data(self):
        return self._signal_data
