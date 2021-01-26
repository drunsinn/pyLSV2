#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests if string translation works"""

import pyLSV2


def test_translation():
    """simple test if the content of error strings changes between languages"""
    text_en = pyLSV2.translate_error.get_error_text(
        error_type=1, error_code=pyLSV2.translate_error.LSV2_ERROR_T_BD_NO_NEW_FILE, lang='en')
    text_de = pyLSV2.translate_error.get_error_text(
        error_type=1, error_code=pyLSV2.translate_error.LSV2_ERROR_T_BD_NO_NEW_FILE, lang='de')

    assert ('LSV2_ERROR_T_BD_NO_NEW_FILE' in text_en) is False
    assert ('LSV2_ERROR_T_BD_NO_NEW_FILE' in text_de) is False
    assert (text_en in text_de) is False
