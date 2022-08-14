#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests if string translation works"""

import pyLSV2


def test_translation():
    """simple test if the content of error strings changes between languages"""
    test_error = pyLSV2.TransmissionError()
    test_error.e_code = pyLSV2.LSV2Err.T_BD_NO_NEW_FILE
    test_error.e_type = 1
    text_en = pyLSV2.get_error_text(test_error, language="en")

    assert ("LSV2_ERROR_T_BD_NO_NEW_FILE" in text_en) is False


def test_state_string_conv():
    """test if conversion of state ids works"""
    text = pyLSV2.get_program_status_text(pyLSV2.PgmState.STOPPED, language="en")
    assert ("PGM_STATE_UNKNOWN" in text) is False

    text = pyLSV2.get_execution_status_text(pyLSV2.ExecState.MDI, language="en")
    assert ("EXEC_STATE_UNKNOWN" in text) is False
