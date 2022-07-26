#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""data classes for pyLSV2"""

import struct
from .const import ControlType


class VersionInfo():
    def __init__(self):
        """data class for version information, uses properties instead o f dataclass for compatibility"""
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
        return self._control_version

    @control_version.setter
    def control_version(self, value: str):
        self._control_version = value

    @property
    def control_type(self) -> ControlType:
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

    def __init__(self):
        """data class for system parameters, uses properties instead o f dataclass for compatibility"""
        inputs_start_address = -1
        number_of_inputs = -1
        outputs_start_address = -1
        number_of_outputs = -1

        counters_start_address = -1
        number_of_counters = -1

        timers_start_address = -1
        number_of_timers = -1

        words_start_address = -1
        number_of_words = -1

        strings_start_address = -1
        number_of_strings = -1
        max_string_lenght = -1

        input_words_start_address = -1
        number_of_input_words = -1

        output_words_start_address = -1
        number_of_output_words = -1

        lsv2_version = -1
        lsv2_version_flags = -1
        lsv2_version_flags_ex = -1

        max_block_length = -1

        bin_version = -1
        bin_revision = -1
        iso_version = -1
        iso_revision = -1

        hardware_version = -1

        max_trace_line = -1
        number_of_scope_channels = -1

        password_encryption_key = -1

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
        """names were choosen so not to interfere with existing names"""
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
