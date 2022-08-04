#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""data classes for pyLSV2"""

from datetime import datetime

from .const import ControlType


class VersionInfo:
    def __init__(self):
        """data class for version information, uses properties instead of dataclass for compatibility"""
        self.control_version = ""
        self.control_type = ControlType.UNKNOWN
        self.nc_version = ""
        self.plc_version = ""
        self.splc_version = ""
        self.option_bits = ""
        self.id_number = ""
        self.release_type = ""

    @property
    def control_version(self) -> str:
        """
        version identifyer of the control

        :getter: returns the version string
        :setter: sets the version string
        """
        return self._control_version

    @control_version.setter
    def control_version(self, value: str):
        self._control_version = value

    @property
    def control_type(self) -> ControlType:
        """
        control type identifyer of the control

        :getter: returns the control type
        :setter: sets the control type
        """
        return self._control_type

    @control_type.setter
    def control_type(self, value: ControlType):
        self._control_type = value

    @property
    def nc_version(self) -> str:
        return self._nc_version

    @nc_version.setter
    def nc_version(self, value: str):
        self._nc_version = value

    @property
    def plc_version(self) -> str:
        return self._plc_version

    @plc_version.setter
    def plc_version(self, value: str):
        self._plc_version = value

    @property
    def splc_version(self) -> str:
        return self._splc_version

    @splc_version.setter
    def splc_version(self, value: str):
        self._splc_version = value

    @property
    def option_bits(self) -> str:
        return self._option_bits

    @option_bits.setter
    def option_bits(self, value: str):
        self._option_bits = value

    @property
    def id_number(self) -> str:
        return self._id_number

    @id_number.setter
    def id_number(self, value: str):
        self._id_number = value

    @property
    def release_type(self) -> str:
        return self._release_type

    @release_type.setter
    def release_type(self, value: str):
        self._release_type = value


class SystemParameters:
    """"""

    def __init__(self):
        """data class for system parameters, uses properties instead o f dataclass for compatibility"""
        self.inputs_start_address = -1
        self.number_of_inputs = -1
        self.outputs_start_address = -1
        self.number_of_outputs = -1

        self.counters_start_address = -1
        self.number_of_counters = -1

        self.timers_start_address = -1
        self.number_of_timers = -1

        self.words_start_address = -1
        self.umber_of_words = -1

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

    @property
    def markers_start_address(self) -> int:
        return self._markers_start_address

    @markers_start_address.setter
    def markers_start_address(self, value: int):
        self._markers_start_address = value

    @property
    def number_of_markers(self) -> int:
        return self._number_of_markers

    @number_of_markers.setter
    def number_of_markers(self, value: int):
        self._number_of_markers = value

    @property
    def inputs_start_address(self) -> int:
        return self._inputs_start_address

    @inputs_start_address.setter
    def inputs_start_address(self, value: int):
        self._inputs_start_address = value

    @property
    def number_of_inputs(self) -> int:
        return self._number_of_inputs

    @number_of_inputs.setter
    def number_of_inputs(self, value: int):
        self._number_of_inputs = value

    @property
    def outputs_start_address(self) -> int:
        return self._outputs_start_address

    @outputs_start_address.setter
    def outputs_start_address(self, value: int):
        self._outputs_start_address = value

    @property
    def number_of_outputs(self) -> int:
        return self._number_of_outputs

    @number_of_outputs.setter
    def number_of_outputs(self, value: int):
        self._number_of_outputs = value

    @property
    def counters_start_address(self) -> int:
        return self._counters_start_address

    @counters_start_address.setter
    def counters_start_address(self, value: int):
        self._counters_start_address = value

    @property
    def number_of_counters(self) -> int:
        return self._number_of_counters

    @number_of_counters.setter
    def number_of_counters(self, value: int):
        self._number_of_counters = value

    @property
    def timers_start_address(self) -> int:
        return self._timers_start_address

    @timers_start_address.setter
    def timers_start_address(self, value: int):
        self._timers_start_address = value

    @property
    def number_of_timers(self) -> int:
        return self._number_of_timers

    @number_of_timers.setter
    def number_of_timers(self, value: int):
        self._number_of_timers = value

    @property
    def words_start_address(self) -> int:
        return self._words_start_address

    @words_start_address.setter
    def words_start_address(self, value: int):
        self._words_start_address = value

    @property
    def number_of_words(self) -> int:
        return self._number_of_words

    @number_of_words.setter
    def number_of_words(self, value: int):
        self._number_of_words = value

    @property
    def strings_start_address(self) -> int:
        return self._strings_start_address

    @strings_start_address.setter
    def strings_start_address(self, value: int):
        self._strings_start_address = value

    @property
    def number_of_strings(self) -> int:
        return self._number_of_strings

    @number_of_strings.setter
    def number_of_strings(self, value: int):
        self._number_of_strings = value

    @property
    def max_string_lenght(self) -> int:
        return self._max_string_lenght

    @max_string_lenght.setter
    def max_string_lenght(self, value: int):
        self._max_string_lenght = value

    @property
    def input_words_start_address(self) -> int:
        return self._input_words_start_address

    @input_words_start_address.setter
    def input_words_start_address(self, value: int):
        self._input_words_start_address = value

    @property
    def number_of_input_words(self) -> int:
        return self._number_of_input_words

    @number_of_input_words.setter
    def number_of_input_words(self, value: int):
        self._number_of_input_words = value

    @property
    def output_words_start_address(self) -> int:
        return self._output_words_start_address

    @output_words_start_address.setter
    def output_words_start_address(self, value: int):
        self._output_words_start_address = value

    @property
    def number_of_output_words(self) -> int:
        return self._number_of_output_words

    @number_of_output_words.setter
    def number_of_output_words(self, value: int):
        self._number_of_output_words = value

    @property
    def lsv2_version(self) -> int:
        return self._lsv2_version

    @lsv2_version.setter
    def lsv2_version(self, value: int):
        self._lsv2_version = value

    @property
    def lsv2_version_flags(self) -> int:
        return self._lsv2_version_flags

    @lsv2_version_flags.setter
    def lsv2_version_flags(self, value: int):
        self._lsv2_version_flags = value

    @property
    def lsv2_version_flags_ex(self) -> int:
        return self._lsv2_version_flags_ex

    @lsv2_version_flags_ex.setter
    def lsv2_version_flags_ex(self, value: int):
        self._lsv2_version_flags_ex = value

    @property
    def max_block_length(self) -> int:
        return self._max_block_length

    @max_block_length.setter
    def max_block_length(self, value: int):
        self._max_block_length = value

    @property
    def bin_version(self) -> int:
        return self._bin_version

    @bin_version.setter
    def bin_version(self, value: int):
        self._bin_version = value

    @property
    def bin_revision(self) -> int:
        return self._bin_revision

    @bin_revision.setter
    def bin_revision(self, value: int):
        self._bin_revision = value

    @property
    def iso_version(self) -> int:
        return self._iso_version

    @iso_version.setter
    def iso_version(self, value: int):
        self._iso_version = value

    @property
    def iso_revision(self) -> int:
        return self._iso_revision

    @iso_revision.setter
    def iso_revision(self, value: int):
        self._iso_revision = value

    @property
    def hardware_version(self) -> int:
        return self._hardware_version

    @hardware_version.setter
    def hardware_version(self, value: int):
        self._hardware_version = value

    @property
    def max_trace_line(self) -> int:
        return self._max_trace_line

    @max_trace_line.setter
    def max_trace_line(self, value: int):
        self._max_trace_line = value

    @property
    def number_of_scope_channels(self) -> int:
        return self._number_of_scope_channels

    @number_of_scope_channels.setter
    def number_of_scope_channels(self, value: int):
        self._number_of_scope_channels = value

    @property
    def password_encryption_key(self) -> int:
        return self._password_encryption_key

    @password_encryption_key.setter
    def password_encryption_key(self, value: int):
        self._password_encryption_key = value


class ToolInformation:
    def __init__(self):
        self.number = -1
        self.index = -1
        self.axis = ""
        self.length = -1
        self.radius = -1
        self.name = ""

    @property
    def number(self) -> int:
        return self._number

    @number.setter
    def number(self, value: int):
        self._number = value

    @property
    def index(self) -> int:
        return self._index

    @index.setter
    def index(self, value: int):
        self._index = value

    @property
    def axis(self) -> str:
        return self._axis

    @axis.setter
    def axis(self, value: str):
        self._axis = value

    @property
    def length(self) -> float:
        return self._length

    @length.setter
    def length(self, value: float):
        self._length = value

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, value: float):
        self._radius = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value


class OverrideState:
    def __init__(self):
        self.feed = -1.0
        self.rapid = -1.0
        self.spindel = -1.0

    @property
    def feed(self) -> float:
        return self._feed

    @feed.setter
    def feed(self, value: float):
        self._feed = value

    @property
    def rapid(self) -> float:
        return self._rapid

    @rapid.setter
    def rapid(self, value: float):
        self._rapid = value

    @property
    def spindel(self) -> float:
        return self._spindel

    @spindel.setter
    def spindel(self, value: float):
        self._spindel = value


class LSV2ErrorMessage:
    def __init__(self):
        """names were chosen so not to interfere with existing names"""
        self.e_class = -1
        self.e_group = -1
        self.e_number = -1
        self.e_text = ""
        self.dnc = False

    @property
    def e_class(self) -> int:
        return self._e_class

    @e_class.setter
    def e_class(self, value: int):
        self._e_class = value

    @property
    def e_group(self) -> int:
        return self._e_group

    @e_group.setter
    def e_group(self, value: int):
        self._e_group = value

    @property
    def e_number(self) -> int:
        return self._e_number

    @e_number.setter
    def e_number(self, value: int):
        self._e_number = value

    @property
    def e_text(self) -> str:
        return self._e_text

    @e_text.setter
    def e_text(self, value: str):
        self._e_text = value

    @property
    def dnc(self) -> bool:
        return self._dnc

    @dnc.setter
    def dnc(self, value: bool):
        self._dnc = value


class StackState:
    def __init__(self):
        self.current_line = -1
        self.main_pgm = ""
        self.current_pgm = ""

    @property
    def current_line(self) -> int:
        return self._current_line

    @current_line.setter
    def current_line(self, value: int):
        self._current_line = value

    @property
    def main_pgm(self) -> str:
        return self._main_pgm

    @main_pgm.setter
    def main_pgm(self, value: str):
        self._main_pgm = value

    @property
    def current_pgm(self) -> str:
        return self._current_pgm

    @current_pgm.setter
    def current_pgm(self, value: str):
        self._current_pgm = value


class FileEntry:
    def __init__(self):
        self.size = -1
        self.timestamp = datetime.fromtimestamp(0)
        self.attributes = bytearray()

        self.is_changable = False
        self.is_drive = False
        self.is_directory = False
        self.is_protected = False
        self.is_hidden = False

        self.name = ""

    @property
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, value: int):
        self._size = value

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value: datetime):
        self._timestamp = value

    @property
    def attributes(self) -> bytearray:
        return self._attributes

    @attributes.setter
    def attributes(self, value: bytearray):
        self._attributes = value

    @property
    def is_protected(self) -> bool:
        return self._is_protected

    @is_protected.setter
    def is_protected(self, value: bool):
        self._is_protected = value

    @property
    def is_drive(self) -> bool:
        return self._is_drive

    @is_drive.setter
    def is_drive(self, value: bool):
        self._is_drive = value

    @property
    def is_directory(self) -> bool:
        return self._is_directory

    @is_directory.setter
    def is_directory(self, value: bool):
        self._is_directory = value

    @property
    def is_hidden(self) -> bool:
        return self._is_hidden

    @is_hidden.setter
    def is_hidden(self, value: bool):
        self._is_hidden = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value


class DirectoryEntry:
    def __init__(self):
        self.free_size = -1
        self.dir_attributes = []
        self.attributes = bytearray()
        self.path = ""

    @property
    def free_size(self) -> int:
        return self._free_size

    @free_size.setter
    def free_size(self, value: int):
        self._free_size = value

    @property
    def dir_attributes(self) -> list:
        return self._dir_attributes

    @dir_attributes.setter
    def dir_attributes(self, value: list):
        self._dir_attributes = value

    @property
    def attributes(self) -> bytearray:
        return self._attributes

    @attributes.setter
    def attributes(self, value: bytearray):
        self._attributes = value

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, value: str):
        self._path = value
