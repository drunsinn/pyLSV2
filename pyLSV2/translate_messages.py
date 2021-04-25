#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""error code definitions and decoding, translation of status information into readable text"""
import gettext
import os
import warnings

from . import const as L_C

# Error map
LSV2_ERROR_T_ER_BAD_FORMAT = 20
LSV2_ERROR_T_ER_UNEXPECTED_TELE = 21
LSV2_ERROR_T_ER_UNKNOWN_TELE = 22
LSV2_ERROR_T_ER_NO_PRIV = 23
LSV2_ERROR_T_ER_WRONG_PARA = 24
LSV2_ERROR_T_ER_BREAK = 25
LSV2_ERROR_T_ER_BAD_KEY = 30
LSV2_ERROR_T_ER_BAD_FNAME = 31
LSV2_ERROR_T_ER_NO_FILE = 32
LSV2_ERROR_T_ER_OPEN_FILE = 33
LSV2_ERROR_T_ER_FILE_EXISTS = 34
LSV2_ERROR_T_ER_BAD_FILE = 35
LSV2_ERROR_T_ER_NO_DELETE = 36
LSV2_ERROR_T_ER_NO_NEW_FILE = 37
LSV2_ERROR_T_ER_NO_CHANGE_ATT = 38
LSV2_ERROR_T_ER_BAD_EMULATEKEY = 39
LSV2_ERROR_T_ER_NO_MP = 40
LSV2_ERROR_T_ER_NO_WIN = 41
LSV2_ERROR_T_ER_WIN_NOT_AKTIV = 42
LSV2_ERROR_T_ER_ANZ = 43
LSV2_ERROR_T_ER_FONT_NOT_DEFINED = 44
LSV2_ERROR_T_ER_FILE_ACCESS = 45
LSV2_ERROR_T_ER_WRONG_DNC_STATUS = 46
LSV2_ERROR_T_ER_CHANGE_PATH = 47
LSV2_ERROR_T_ER_NO_RENAME = 48
LSV2_ERROR_T_ER_NO_LOGIN = 49
LSV2_ERROR_T_ER_BAD_PARAMETER = 50
LSV2_ERROR_T_ER_BAD_NUMBER_FORMAT = 51
LSV2_ERROR_T_ER_BAD_MEMADR = 52
LSV2_ERROR_T_ER_NO_FREE_SPACE = 53
LSV2_ERROR_T_ER_DEL_DIR = 54
LSV2_ERROR_T_ER_NO_DIR = 55
LSV2_ERROR_T_ER_OPERATING_MODE = 56
LSV2_ERROR_T_ER_NO_NEXT_ERROR = 57
LSV2_ERROR_T_ER_ACCESS_TIMEOUT = 58
LSV2_ERROR_T_ER_NO_WRITE_ACCESS = 59
LSV2_ERROR_T_ER_STIB = 60
LSV2_ERROR_T_ER_REF_NECESSARY = 61
LSV2_ERROR_T_ER_PLC_BUF_FULL = 62
LSV2_ERROR_T_ER_NOT_FOUND = 63
LSV2_ERROR_T_ER_WRONG_FILE = 64
LSV2_ERROR_T_ER_NO_MATCH = 65
LSV2_ERROR_T_ER_TOO_MANY_TPTS = 66
LSV2_ERROR_T_ER_NOT_ACTIVATED = 67
LSV2_ERROR_T_ER_DSP_CHANNEL = 70
LSV2_ERROR_T_ER_DSP_PARA = 71
LSV2_ERROR_T_ER_OUT_OF_RANGE = 72
LSV2_ERROR_T_ER_INVALID_AXIS = 73
LSV2_ERROR_T_ER_STREAMING_ACTIVE = 74
LSV2_ERROR_T_ER_NO_STREAMING_ACTIVE = 75
LSV2_ERROR_T_ER_TO_MANY_OPEN_TCP = 80
LSV2_ERROR_T_ER_NO_FREE_HANDLE = 81
LSV2_ERROR_T_ER_PLCMEMREMA_CLEAR = 82
LSV2_ERROR_T_ER_OSZI_CHSEL = 83
LSV2_ERROR_LSV2_BUSY = 90
LSV2_ERROR_LSV2_X_BUSY = 91
LSV2_ERROR_LSV2_NOCONNECT = 92
LSV2_ERROR_LSV2_BAD_BACKUP_FILE = 93
LSV2_ERROR_LSV2_RESTORE_NOT_FOUND = 94
LSV2_ERROR_LSV2_DLL_NOT_INSTALLED = 95
LSV2_ERROR_LSV2_BAD_CONVERT_DLL = 96
LSV2_ERROR_LSV2_BAD_BACKUP_LIST = 97
LSV2_ERROR_LSV2_UNKNOWN_ERROR = 99
LSV2_ERROR_T_BD_NO_NEW_FILE = 100
LSV2_ERROR_T_BD_NO_FREE_SPACE = 101
LSV2_ERROR_T_BD_FILE_NOT_ALLOWED = 102
LSV2_ERROR_T_BD_BAD_FORMAT = 103
LSV2_ERROR_T_BD_BAD_BLOCK = 104
LSV2_ERROR_T_BD_END_PGM = 105
LSV2_ERROR_T_BD_ANZ = 106
LSV2_ERROR_T_BD_WIN_NOT_DEFINED = 107
LSV2_ERROR_T_BD_WIN_CHANGED = 108
LSV2_ERROR_T_BD_DNC_WAIT = 110
LSV2_ERROR_T_BD_CANCELLED = 111
LSV2_ERROR_T_BD_OSZI_OVERRUN = 112
LSV2_ERROR_T_BD_FD = 200
LSV2_ERROR_T_USER_ERROR = 255


def get_error_text(error_type, error_code, language='en'):
    """Parse error type and error code and return the error message.

    :param int error_type: type of error code.
    :param int error_code: code of error message.
    :param str language: language code for message.
    :raise: NotImplementedError if error type is != 1
    :return: error message in selected language
    :rtype: str
    """
    warnings.warn('Deprecation Warning! The definition of the LSV2_ERROR_ constants was extracted from pyLSV.translate_mesages to pyLSV2. Definition in LSV2 will be removed in future versions')

    locale_path = os.path.dirname(__file__) + '/locales'
    translate = gettext.translation(
        'error_text', localedir=locale_path, languages=[language], fallback=True)
    _ = translate.gettext

    if error_type != 1:
        raise NotImplementedError('Unknown error type: %d' % error_type)
    return {L_C.LSV2_ERROR_T_ER_BAD_FORMAT: _('LSV2_ERROR_T_ER_BAD_FORMAT'),
            L_C.LSV2_ERROR_T_ER_UNEXPECTED_TELE: _('LSV2_ERROR_T_ER_UNEXPECTED_TELE'),
            L_C.LSV2_ERROR_T_ER_UNKNOWN_TELE: _('LSV2_ERROR_T_ER_UNKNOWN_TELE'),
            L_C.LSV2_ERROR_T_ER_NO_PRIV: _('LSV2_ERROR_T_ER_NO_PRIV'),
            L_C.LSV2_ERROR_T_ER_WRONG_PARA: _('LSV2_ERROR_T_ER_WRONG_PARA'),
            L_C.LSV2_ERROR_T_ER_BREAK: _('LSV2_ERROR_T_ER_BREAK'),
            L_C.LSV2_ERROR_T_ER_BAD_KEY: _('LSV2_ERROR_T_ER_BAD_KEY'),
            L_C.LSV2_ERROR_T_ER_BAD_FNAME: _('LSV2_ERROR_T_ER_BAD_FNAME'),
            L_C.LSV2_ERROR_T_ER_NO_FILE: _('LSV2_ERROR_T_ER_NO_FILE'),
            L_C.LSV2_ERROR_T_ER_OPEN_FILE: _('LSV2_ERROR_T_ER_OPEN_FILE'),
            L_C.LSV2_ERROR_T_ER_FILE_EXISTS: _('LSV2_ERROR_T_ER_FILE_EXISTS'),
            L_C.LSV2_ERROR_T_ER_BAD_FILE: _('LSV2_ERROR_T_ER_BAD_FILE'),
            L_C.LSV2_ERROR_T_ER_NO_DELETE: _('LSV2_ERROR_T_ER_NO_DELETE'),
            L_C.LSV2_ERROR_T_ER_NO_NEW_FILE: _('LSV2_ERROR_T_ER_NO_NEW_FILE'),
            L_C.LSV2_ERROR_T_ER_NO_CHANGE_ATT: _('LSV2_ERROR_T_ER_NO_CHANGE_ATT'),
            L_C.LSV2_ERROR_T_ER_BAD_EMULATEKEY: _('LSV2_ERROR_T_ER_BAD_EMULATEKEY'),
            L_C.LSV2_ERROR_T_ER_NO_MP: _('LSV2_ERROR_T_ER_NO_MP'),
            L_C.LSV2_ERROR_T_ER_NO_WIN: _('LSV2_ERROR_T_ER_NO_WIN'),
            L_C.LSV2_ERROR_T_ER_WIN_NOT_AKTIV: _('LSV2_ERROR_T_ER_WIN_NOT_AKTIV'),
            L_C.LSV2_ERROR_T_ER_ANZ: _('LSV2_ERROR_T_ER_ANZ'),
            L_C.LSV2_ERROR_T_ER_FONT_NOT_DEFINED: _('LSV2_ERROR_T_ER_FONT_NOT_DEFINED'),
            L_C.LSV2_ERROR_T_ER_FILE_ACCESS: _('LSV2_ERROR_T_ER_FILE_ACCESS'),
            L_C.LSV2_ERROR_T_ER_WRONG_DNC_STATUS: _('LSV2_ERROR_T_ER_WRONG_DNC_STATUS'),
            L_C.LSV2_ERROR_T_ER_CHANGE_PATH: _('LSV2_ERROR_T_ER_CHANGE_PATH'),
            L_C.LSV2_ERROR_T_ER_NO_RENAME: _('LSV2_ERROR_T_ER_NO_RENAME'),
            L_C.LSV2_ERROR_T_ER_NO_LOGIN: _('LSV2_ERROR_T_ER_NO_LOGIN'),
            L_C.LSV2_ERROR_T_ER_BAD_PARAMETER: _('LSV2_ERROR_T_ER_BAD_PARAMETER'),
            L_C.LSV2_ERROR_T_ER_BAD_NUMBER_FORMAT: _('LSV2_ERROR_T_ER_BAD_NUMBER_FORMAT'),
            L_C.LSV2_ERROR_T_ER_BAD_MEMADR: _('LSV2_ERROR_T_ER_BAD_MEMADR'),
            L_C.LSV2_ERROR_T_ER_NO_FREE_SPACE: _('LSV2_ERROR_T_ER_NO_FREE_SPACE'),
            L_C.LSV2_ERROR_T_ER_DEL_DIR: _('LSV2_ERROR_T_ER_DEL_DIR'),
            L_C.LSV2_ERROR_T_ER_NO_DIR: _('LSV2_ERROR_T_ER_NO_DIR'),
            L_C.LSV2_ERROR_T_ER_OPERATING_MODE: _('LSV2_ERROR_T_ER_OPERATING_MODE'),
            L_C.LSV2_ERROR_T_ER_NO_NEXT_ERROR: _('LSV2_ERROR_T_ER_NO_NEXT_ERROR'),
            L_C.LSV2_ERROR_T_ER_ACCESS_TIMEOUT: _('LSV2_ERROR_T_ER_ACCESS_TIMEOUT'),
            L_C.LSV2_ERROR_T_ER_NO_WRITE_ACCESS: _('LSV2_ERROR_T_ER_NO_WRITE_ACCESS'),
            L_C.LSV2_ERROR_T_ER_STIB: _('LSV2_ERROR_T_ER_STIB'),
            L_C.LSV2_ERROR_T_ER_REF_NECESSARY: _('LSV2_ERROR_T_ER_REF_NECESSARY'),
            L_C.LSV2_ERROR_T_ER_PLC_BUF_FULL: _('LSV2_ERROR_T_ER_PLC_BUF_FULL'),
            L_C.LSV2_ERROR_T_ER_NOT_FOUND: _('LSV2_ERROR_T_ER_NOT_FOUND'),
            L_C.LSV2_ERROR_T_ER_WRONG_FILE: _('LSV2_ERROR_T_ER_WRONG_FILE'),
            L_C.LSV2_ERROR_T_ER_NO_MATCH: _('LSV2_ERROR_T_ER_NO_MATCH'),
            L_C.LSV2_ERROR_T_ER_TOO_MANY_TPTS: _('LSV2_ERROR_T_ER_TOO_MANY_TPTS'),
            L_C.LSV2_ERROR_T_ER_NOT_ACTIVATED: _('LSV2_ERROR_T_ER_NOT_ACTIVATED'),
            L_C.LSV2_ERROR_T_ER_DSP_CHANNEL: _('LSV2_ERROR_T_ER_DSP_CHANNEL'),
            L_C.LSV2_ERROR_T_ER_DSP_PARA: _('LSV2_ERROR_T_ER_DSP_PARA'),
            L_C.LSV2_ERROR_T_ER_OUT_OF_RANGE: _('LSV2_ERROR_T_ER_OUT_OF_RANGE'),
            L_C.LSV2_ERROR_T_ER_INVALID_AXIS: _('LSV2_ERROR_T_ER_INVALID_AXIS'),
            L_C.LSV2_ERROR_T_ER_STREAMING_ACTIVE: _('LSV2_ERROR_T_ER_STREAMING_ACTIVE'),
            L_C.LSV2_ERROR_T_ER_NO_STREAMING_ACTIVE: _('LSV2_ERROR_T_ER_NO_STREAMING_ACTIVE'),
            L_C.LSV2_ERROR_T_ER_TO_MANY_OPEN_TCP: _('LSV2_ERROR_T_ER_TO_MANY_OPEN_TCP'),
            L_C.LSV2_ERROR_T_ER_NO_FREE_HANDLE: _('LSV2_ERROR_T_ER_NO_FREE_HANDLE'),
            L_C.LSV2_ERROR_T_ER_PLCMEMREMA_CLEAR: _('LSV2_ERROR_T_ER_PLCMEMREMA_CLEAR'),
            L_C.LSV2_ERROR_T_ER_OSZI_CHSEL: _('LSV2_ERROR_T_ER_OSZI_CHSEL'),
            L_C.LSV2_ERROR_LSV2_BUSY: _('LSV2_ERROR_LSV2_BUSY'),
            L_C.LSV2_ERROR_LSV2_X_BUSY: _('LSV2_ERROR_LSV2_X_BUSY'),
            L_C.LSV2_ERROR_LSV2_NOCONNECT: _('LSV2_ERROR_LSV2_NOCONNECT'),
            L_C.LSV2_ERROR_LSV2_BAD_BACKUP_FILE: _('LSV2_ERROR_LSV2_BAD_BACKUP_FILE'),
            L_C.LSV2_ERROR_LSV2_RESTORE_NOT_FOUND: _('LSV2_ERROR_LSV2_RESTORE_NOT_FOUND'),
            L_C.LSV2_ERROR_LSV2_DLL_NOT_INSTALLED: _('LSV2_ERROR_LSV2_DLL_NOT_INSTALLED'),
            L_C.LSV2_ERROR_LSV2_BAD_CONVERT_DLL: _('LSV2_ERROR_LSV2_BAD_CONVERT_DLL'),
            L_C.LSV2_ERROR_LSV2_BAD_BACKUP_LIST: _('LSV2_ERROR_LSV2_BAD_BACKUP_LIST'),
            L_C.LSV2_ERROR_LSV2_UNKNOWN_ERROR: _('LSV2_ERROR_LSV2_UNKNOWN_ERROR'),
            L_C.LSV2_ERROR_T_BD_NO_NEW_FILE: _('LSV2_ERROR_T_BD_NO_NEW_FILE'),
            L_C.LSV2_ERROR_T_BD_NO_FREE_SPACE: _('LSV2_ERROR_T_BD_NO_FREE_SPACE'),
            L_C.LSV2_ERROR_T_BD_FILE_NOT_ALLOWED: _('LSV2_ERROR_T_BD_FILE_NOT_ALLOWED'),
            L_C.LSV2_ERROR_T_BD_BAD_FORMAT: _('LSV2_ERROR_T_BD_BAD_FORMAT'),
            L_C.LSV2_ERROR_T_BD_BAD_BLOCK: _('LSV2_ERROR_T_BD_BAD_BLOCK'),
            L_C.LSV2_ERROR_T_BD_END_PGM: _('LSV2_ERROR_T_BD_END_PGM'),
            L_C.LSV2_ERROR_T_BD_ANZ: _('LSV2_ERROR_T_BD_ANZ'),
            L_C.LSV2_ERROR_T_BD_WIN_NOT_DEFINED: _('LSV2_ERROR_T_BD_WIN_NOT_DEFINED'),
            L_C.LSV2_ERROR_T_BD_WIN_CHANGED: _('LSV2_ERROR_T_BD_WIN_CHANGED'),
            L_C.LSV2_ERROR_T_BD_DNC_WAIT: _('LSV2_ERROR_T_BD_DNC_WAIT'),
            L_C.LSV2_ERROR_T_BD_CANCELLED: _('LSV2_ERROR_T_BD_CANCELLED'),
            L_C.LSV2_ERROR_T_BD_OSZI_OVERRUN: _('LSV2_ERROR_T_BD_OSZI_OVERRUN'),
            L_C.LSV2_ERROR_T_BD_FD: _('LSV2_ERROR_T_BD_FD'),
            L_C.LSV2_ERROR_T_USER_ERROR: _('LSV2_ERROR_T_USER_ERROR')}.get(error_code, _('LSV2_ERROR_UNKNOWN_CODE'))


def get_program_status_text(code, language='en'):
    """Translate status code of program state to text

    :param int code: status code of program state
    :param str language: optional. language code for translation of text
    :returns: readable text for execution state
    :rtype: str
    """
    locale_path = os.path.dirname(__file__) + '/locales'
    translate = gettext.translation(
        'message_text', localedir=locale_path, languages=[language], fallback=True)
    return {L_C.PGM_STATE_STARTED: translate.gettext('PGM_STATE_STARTED'),
            L_C.PGM_STATE_STOPPED: translate.gettext('PGM_STATE_STOPPED'),
            L_C.PGM_STATE_FINISHED: translate.gettext('PGM_STATE_FINISHED'),
            L_C.PGM_STATE_CANCELLED: translate.gettext('PGM_STATE_CANCELLED'),
            L_C.PGM_STATE_INTERRUPTED: translate.gettext('PGM_STATE_INTERRUPTED'),
            L_C.PGM_STATE_ERROR: translate.gettext('PGM_STATE_ERROR'),
            L_C.PGM_STATE_ERROR_CLEARED: translate.gettext('PGM_STATE_ERROR_CLEARED'),
            L_C.PGM_STATE_IDLE: translate.gettext('PGM_STATE_IDLE'),
            L_C.PGM_STATE_UNDEFINED: translate.gettext('PGM_STATE_UNDEFINED')}.get(code, translate.gettext('PGM_STATE_UNKNOWN'))

def get_execution_status_text(code, language='en'):
    """Translate status code of execution state to text
    See https://github.com/drunsinn/pyLSV2/issues/1

    :param int code: status code of execution status
    :param str language: optional. language code for translation of text
    :returns: readable text for execution state
    :rtype: str
    """
    locale_path = os.path.dirname(__file__) + '/locales'
    translate = gettext.translation(
        'message_text', localedir=locale_path, languages=[language], fallback=True)
    return {L_C.EXEC_STATE_MANUAL: translate.gettext('EXEC_STATE_MANUAL'),
            L_C.EXEC_STATE_MDI: translate.gettext('EXEC_STATE_MDI'),
            L_C.EXEC_STATE_PASS_REFERENCES: translate.gettext('EXEC_STATE_PASS_REFERENCES'),
            L_C.EXEC_STATE_SINGLE_STEP: translate.gettext('EXEC_STATE_SINGLE_STEP'),
            L_C.EXEC_STATE_AUTOMATIC: translate.gettext('EXEC_STATE_AUTOMATIC'),
            L_C.EXEC_STATE_UNDEFINED: translate.gettext('EXEC_STATE_UNDEFINED')}.get(code, translate.gettext('EXEC_STATE_UNKNOWN'))
