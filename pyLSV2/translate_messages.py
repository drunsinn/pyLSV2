#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""error code definitions and decoding, translation of status information into readable text"""

import gettext
import os
from typing import Union

from .dat_cls import LSV2Error

from .const import ExecState, LSV2StatusCode, PgmState


def get_error_text(t_error: LSV2Error, language: str = "", locale_path: Union[str, None] = None) -> str:
    """Parse error type and error code and return the error message.

    :param int error_type: type of error code.
    :param int error_code: code of error message.
    :param str language: language code for message.
    :raise: NotImplementedError if error type is != 1
    :return: error message in selected language
    :rtype: str
    """

    if locale_path is None:
        locale_path = os.path.join(os.path.dirname(__file__), "locales")

    if len(language) < 2:
        translate = gettext.translation(domain="error_text", localedir=locale_path, fallback=True)
    else:
        translate = gettext.translation(
            domain="error_text",
            localedir=locale_path,
            fallback=True,
            languages=[
                language,
            ],
        )
    _ = translate.gettext

    if t_error.e_type != 1:
        raise NotImplementedError("Unknown error type: %d" % t_error.e_type)
    return {
        LSV2StatusCode.T_ER_BAD_FORMAT: _("LSV2_ERROR_T_ER_BAD_FORMAT"),
        LSV2StatusCode.T_ER_UNEXPECTED_TELE: _("LSV2_ERROR_T_ER_UNEXPECTED_TELE"),
        LSV2StatusCode.T_ER_UNKNOWN_TELE: _("LSV2_ERROR_T_ER_UNKNOWN_TELE"),
        LSV2StatusCode.T_ER_NO_PRIV: _("LSV2_ERROR_T_ER_NO_PRIV"),
        LSV2StatusCode.T_ER_WRONG_PARA: _("LSV2_ERROR_T_ER_WRONG_PARA"),
        LSV2StatusCode.T_ER_BREAK: _("LSV2_ERROR_T_ER_BREAK"),
        LSV2StatusCode.T_ER_BAD_KEY: _("LSV2_ERROR_T_ER_BAD_KEY"),
        LSV2StatusCode.T_ER_BAD_FNAME: _("LSV2_ERROR_T_ER_BAD_FNAME"),
        LSV2StatusCode.T_ER_NO_FILE: _("LSV2_ERROR_T_ER_NO_FILE"),
        LSV2StatusCode.T_ER_OPEN_FILE: _("LSV2_ERROR_T_ER_OPEN_FILE"),
        LSV2StatusCode.T_ER_FILE_EXISTS: _("LSV2_ERROR_T_ER_FILE_EXISTS"),
        LSV2StatusCode.T_ER_BAD_FILE: _("LSV2_ERROR_T_ER_BAD_FILE"),
        LSV2StatusCode.T_ER_NO_DELETE: _("LSV2_ERROR_T_ER_NO_DELETE"),
        LSV2StatusCode.T_ER_NO_NEW_FILE: _("LSV2_ERROR_T_ER_NO_NEW_FILE"),
        LSV2StatusCode.T_ER_NO_CHANGE_ATT: _("LSV2_ERROR_T_ER_NO_CHANGE_ATT"),
        LSV2StatusCode.T_ER_BAD_EMULATEKEY: _("LSV2_ERROR_T_ER_BAD_EMULATEKEY"),
        LSV2StatusCode.T_ER_NO_MP: _("LSV2_ERROR_T_ER_NO_MP"),
        LSV2StatusCode.T_ER_NO_WIN: _("LSV2_ERROR_T_ER_NO_WIN"),
        LSV2StatusCode.T_ER_WIN_NOT_AKTIV: _("LSV2_ERROR_T_ER_WIN_NOT_AKTIV"),
        LSV2StatusCode.T_ER_ANZ: _("LSV2_ERROR_T_ER_ANZ"),
        LSV2StatusCode.T_ER_FONT_NOT_DEFINED: _("LSV2_ERROR_T_ER_FONT_NOT_DEFINED"),
        LSV2StatusCode.T_ER_FILE_ACCESS: _("LSV2_ERROR_T_ER_FILE_ACCESS"),
        LSV2StatusCode.T_ER_WRONG_DNC_STATUS: _("LSV2_ERROR_T_ER_WRONG_DNC_STATUS"),
        LSV2StatusCode.T_ER_CHANGE_PATH: _("LSV2_ERROR_T_ER_CHANGE_PATH"),
        LSV2StatusCode.T_ER_NO_RENAME: _("LSV2_ERROR_T_ER_NO_RENAME"),
        LSV2StatusCode.T_ER_NO_LOGIN: _("LSV2_ERROR_T_ER_NO_LOGIN"),
        LSV2StatusCode.T_ER_BAD_PARAMETER: _("LSV2_ERROR_T_ER_BAD_PARAMETER"),
        LSV2StatusCode.T_ER_BAD_NUMBER_FORMAT: _("LSV2_ERROR_T_ER_BAD_NUMBER_FORMAT"),
        LSV2StatusCode.T_ER_BAD_MEMADR: _("LSV2_ERROR_T_ER_BAD_MEMADR"),
        LSV2StatusCode.T_ER_NO_FREE_SPACE: _("LSV2_ERROR_T_ER_NO_FREE_SPACE"),
        LSV2StatusCode.T_ER_DEL_DIR: _("LSV2_ERROR_T_ER_DEL_DIR"),
        LSV2StatusCode.T_ER_NO_DIR: _("LSV2_ERROR_T_ER_NO_DIR"),
        LSV2StatusCode.T_ER_OPERATING_MODE: _("LSV2_ERROR_T_ER_OPERATING_MODE"),
        LSV2StatusCode.T_ER_NO_NEXT_ERROR: _("LSV2_ERROR_T_ER_NO_NEXT_ERROR"),
        LSV2StatusCode.T_ER_ACCESS_TIMEOUT: _("LSV2_ERROR_T_ER_ACCESS_TIMEOUT"),
        LSV2StatusCode.T_ER_NO_WRITE_ACCESS: _("LSV2_ERROR_T_ER_NO_WRITE_ACCESS"),
        LSV2StatusCode.T_ER_STIB: _("LSV2_ERROR_T_ER_STIB"),
        LSV2StatusCode.T_ER_REF_NECESSARY: _("LSV2_ERROR_T_ER_REF_NECESSARY"),
        LSV2StatusCode.T_ER_PLC_BUF_FULL: _("LSV2_ERROR_T_ER_PLC_BUF_FULL"),
        LSV2StatusCode.T_ER_NOT_FOUND: _("LSV2_ERROR_T_ER_NOT_FOUND"),
        LSV2StatusCode.T_ER_WRONG_FILE: _("LSV2_ERROR_T_ER_WRONG_FILE"),
        LSV2StatusCode.T_ER_NO_MATCH: _("LSV2_ERROR_T_ER_NO_MATCH"),
        LSV2StatusCode.T_ER_TOO_MANY_TPTS: _("LSV2_ERROR_T_ER_TOO_MANY_TPTS"),
        LSV2StatusCode.T_ER_NOT_ACTIVATED: _("LSV2_ERROR_T_ER_NOT_ACTIVATED"),
        LSV2StatusCode.T_ER_DSP_CHANNEL: _("LSV2_ERROR_T_ER_DSP_CHANNEL"),
        LSV2StatusCode.T_ER_DSP_PARA: _("LSV2_ERROR_T_ER_DSP_PARA"),
        LSV2StatusCode.T_ER_OUT_OF_RANGE: _("LSV2_ERROR_T_ER_OUT_OF_RANGE"),
        LSV2StatusCode.T_ER_INVALID_AXIS: _("LSV2_ERROR_T_ER_INVALID_AXIS"),
        LSV2StatusCode.T_ER_STREAMING_ACTIVE: _("LSV2_ERROR_T_ER_STREAMING_ACTIVE"),
        LSV2StatusCode.T_ER_NO_STREAMING_ACTIVE: _("LSV2_ERROR_T_ER_NO_STREAMING_ACTIVE"),
        LSV2StatusCode.T_ER_TO_MANY_OPEN_TCP: _("LSV2_ERROR_T_ER_TO_MANY_OPEN_TCP"),
        LSV2StatusCode.T_ER_NO_FREE_HANDLE: _("LSV2_ERROR_T_ER_NO_FREE_HANDLE"),
        LSV2StatusCode.T_ER_PLCMEMREMA_CLEAR: _("LSV2_ERROR_T_ER_PLCMEMREMA_CLEAR"),
        LSV2StatusCode.T_ER_OSZI_CHSEL: _("LSV2_ERROR_T_ER_OSZI_CHSEL"),
        LSV2StatusCode.LSV2_BUSY: _("LSV2_ERROR_LSV2_BUSY"),
        LSV2StatusCode.LSV2_X_BUSY: _("LSV2_ERROR_LSV2_X_BUSY"),
        LSV2StatusCode.LSV2_NOCONNECT: _("LSV2_ERROR_LSV2_NOCONNECT"),
        LSV2StatusCode.LSV2_BAD_BACKUP_FILE: _("LSV2_ERROR_LSV2_BAD_BACKUP_FILE"),
        LSV2StatusCode.LSV2_RESTORE_NOT_FOUND: _("LSV2_ERROR_LSV2_RESTORE_NOT_FOUND"),
        LSV2StatusCode.LSV2_DLL_NOT_INSTALLED: _("LSV2_ERROR_LSV2_DLL_NOT_INSTALLED"),
        LSV2StatusCode.LSV2_BAD_CONVERT_DLL: _("LSV2_ERROR_LSV2_BAD_CONVERT_DLL"),
        LSV2StatusCode.LSV2_BAD_BACKUP_LIST: _("LSV2_ERROR_LSV2_BAD_BACKUP_LIST"),
        LSV2StatusCode.LSV2_UNKNOWN_ERROR: _("LSV2_ERROR_LSV2_UNKNOWN_ERROR"),
        LSV2StatusCode.T_BD_NO_NEW_FILE: _("LSV2_ERROR_T_BD_NO_NEW_FILE"),
        LSV2StatusCode.T_BD_NO_FREE_SPACE: _("LSV2_ERROR_T_BD_NO_FREE_SPACE"),
        LSV2StatusCode.T_BD_FILE_NOT_ALLOWED: _("LSV2_ERROR_T_BD_FILE_NOT_ALLOWED"),
        LSV2StatusCode.T_BD_BAD_FORMAT: _("LSV2_ERROR_T_BD_BAD_FORMAT"),
        LSV2StatusCode.T_BD_BAD_BLOCK: _("LSV2_ERROR_T_BD_BAD_BLOCK"),
        LSV2StatusCode.T_BD_END_PGM: _("LSV2_ERROR_T_BD_END_PGM"),
        LSV2StatusCode.T_BD_ANZ: _("LSV2_ERROR_T_BD_ANZ"),
        LSV2StatusCode.T_BD_WIN_NOT_DEFINED: _("LSV2_ERROR_T_BD_WIN_NOT_DEFINED"),
        LSV2StatusCode.T_BD_WIN_CHANGED: _("LSV2_ERROR_T_BD_WIN_CHANGED"),
        LSV2StatusCode.T_BD_DNC_WAIT: _("LSV2_ERROR_T_BD_DNC_WAIT"),
        LSV2StatusCode.T_BD_CANCELLED: _("LSV2_ERROR_T_BD_CANCELLED"),
        LSV2StatusCode.T_BD_OSZI_OVERRUN: _("LSV2_ERROR_T_BD_OSZI_OVERRUN"),
        LSV2StatusCode.T_BD_FD: _("LSV2_ERROR_T_BD_FD"),
        LSV2StatusCode.T_USER_ERROR: _("LSV2_ERROR_T_USER_ERROR"),
    }.get(t_error.e_code, _("LSV2_ERROR_UNKNOWN_CODE"))


def get_program_status_text(code: PgmState, language: str = "", locale_path: Union[str, None] = None) -> str:
    """Translate status code of program state to text

    :param int code: status code of program state
    :param str language: optional. language code for translation of text
    :returns: readable text for execution state
    :rtype: str
    """

    if locale_path is None:
        locale_path = os.path.join(os.path.dirname(__file__), "locales")

    if len(language) < 2:
        translate = gettext.translation(domain="message_text", localedir=locale_path, fallback=True)
    else:
        translate = gettext.translation(
            domain="message_text",
            localedir=locale_path,
            fallback=True,
            languages=[
                language,
            ],
        )
    _ = translate.gettext

    return {
        PgmState.STARTED: translate.gettext("PGM_STATE_STARTED"),
        PgmState.STOPPED: translate.gettext("PGM_STATE_STOPPED"),
        PgmState.FINISHED: translate.gettext("PGM_STATE_FINISHED"),
        PgmState.CANCELLED: translate.gettext("PGM_STATE_CANCELLED"),
        PgmState.INTERRUPTED: translate.gettext("PGM_STATE_INTERRUPTED"),
        PgmState.ERROR: translate.gettext("PGM_STATE_ERROR"),
        PgmState.ERROR_CLEARED: translate.gettext("PGM_STATE_ERROR_CLEARED"),
        PgmState.IDLE: translate.gettext("PGM_STATE_IDLE"),
        PgmState.UNDEFINED: translate.gettext("PGM_STATE_UNDEFINED"),
    }.get(code, translate.gettext("PGM_STATE_UNKNOWN"))


def get_execution_status_text(code: ExecState, language: str = "", locale_path: Union[str, None] = None):
    """Translate status code of execution state to text
    See https://github.com/drunsinn/pyLSV2/issues/1

    :param int code: status code of execution status
    :param str language: optional. language code for translation of text
    :returns: readable text for execution state
    :rtype: str
    """

    if locale_path is None:
        locale_path = os.path.join(os.path.dirname(__file__), "locales")

    if len(language) < 2:
        translate = gettext.translation(domain="message_text", localedir=locale_path, fallback=True)
    else:
        translate = gettext.translation(
            domain="message_text",
            localedir=locale_path,
            fallback=True,
            languages=[
                language,
            ],
        )
    _ = translate.gettext

    return {
        ExecState.MANUAL: translate.gettext("EXEC_STATE_MANUAL"),
        ExecState.MDI: translate.gettext("EXEC_STATE_MDI"),
        ExecState.PASS_REFERENCES: translate.gettext("EXEC_STATE_PASS_REFERENCES"),
        ExecState.SINGLE_STEP: translate.gettext("EXEC_STATE_SINGLE_STEP"),
        ExecState.AUTOMATIC: translate.gettext("EXEC_STATE_AUTOMATIC"),
        ExecState.UNDEFINED: translate.gettext("EXEC_STATE_UNDEFINED"),
    }.get(code, translate.gettext("EXEC_STATE_UNKNOWN"))
