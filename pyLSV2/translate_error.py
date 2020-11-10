#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""error code definitions and decoding"""

#Error map
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


def get_error_text(error_type, error_code, lang='en'):
    """parse the error code and return the error message."""
    if error_type != 1:
        raise Exception('unknown first bit in error message')
    if lang in 'de':
        return {LSV2_ERROR_T_ER_BAD_FORMAT: 'Formatfehler im Telegramm',
            LSV2_ERROR_T_ER_UNEXPECTED_TELE: 'gesendetes Telegram passt nicht zum Protokoll',
            LSV2_ERROR_T_ER_UNKNOWN_TELE: 'Telegrammtyp nicht bekannt',
            LSV2_ERROR_T_ER_NO_PRIV: 'Kein Privileg für Ausführung',
            LSV2_ERROR_T_ER_WRONG_PARA: 'Parameter nicht zulässig',
            LSV2_ERROR_T_ER_BREAK: 'Vom Benutzer abgebrochen',
            LSV2_ERROR_T_ER_BAD_KEY: 'falsche Schlüsselzahl für Login',
            LSV2_ERROR_T_ER_BAD_FNAME: 'Dateiname / Pfadname nicht zulässig',
            LSV2_ERROR_T_ER_NO_FILE: 'Datei existiert nicht',
            LSV2_ERROR_T_ER_OPEN_FILE: 'Datei kann nicht geöffnet werden',
            LSV2_ERROR_T_ER_FILE_EXISTS: 'Datei existiert bereits',
            LSV2_ERROR_T_ER_BAD_FILE: 'Dateityp darf nicht geladen werden (z.B. Programmname == Userzyklusname) oder Dateityp nicht bekannt oder Dateityp gesperrt',
            LSV2_ERROR_T_ER_NO_DELETE: 'Datei kann nicht gelöscht werden',
            LSV2_ERROR_T_ER_NO_NEW_FILE: 'Datei kann nicht angelegt werden',
            LSV2_ERROR_T_ER_NO_CHANGE_ATT: 'Readonly Attrib. kann nicht verändert werden',
            LSV2_ERROR_T_ER_BAD_EMULATEKEY: 'Tastenemulation fehlerhaft',
            LSV2_ERROR_T_ER_NO_MP: 'Maschinenparameter nicht vorhanden oder nicht interpretierbar',
            LSV2_ERROR_T_ER_NO_WIN: 'falsche Window- oder Screennummer',
            LSV2_ERROR_T_ER_WIN_NOT_AKTIV: 'Window nicht aktiv',
            LSV2_ERROR_T_ER_ANZ: 'Fehler bei Befehlsabarbeitung in der Anzeigetask',
            LSV2_ERROR_T_ER_FONT_NOT_DEFINED: 'Anfrage eines nicht vorhandenen Fonts',
            LSV2_ERROR_T_ER_FILE_ACCESS: 'Fehler beim Dateizugriff',
            LSV2_ERROR_T_ER_WRONG_DNC_STATUS: 'Telegramm im aktuellen DNC-Zustand nicht zulässig',
            LSV2_ERROR_T_ER_CHANGE_PATH: 'Verzeichniswechsel nicht möglich',
            LSV2_ERROR_T_ER_NO_RENAME: 'Umbenennen nicht möglich',
            LSV2_ERROR_T_ER_NO_LOGIN: 'Login mit angegebenem Privileg nicht möglich (z.B. dieses schon an andere Schnittstelle vergeben)',
            LSV2_ERROR_T_ER_BAD_PARAMETER: 'Parameter im Telegram nicht o.k.',
            LSV2_ERROR_T_ER_BAD_NUMBER_FORMAT: 'Falsches Zahlenformat',
            LSV2_ERROR_T_ER_BAD_MEMADR: 'Falsche Speicheradresse',
            LSV2_ERROR_T_ER_NO_FREE_SPACE: 'Nicht genug Speicher',
            LSV2_ERROR_T_ER_DEL_DIR: 'Verzeichnis kann nicht gelöscht werden',
            LSV2_ERROR_T_ER_NO_DIR: 'Verzeichnis nicht vorhanden',
            LSV2_ERROR_T_ER_OPERATING_MODE: 'Falsche Betriebsart',
            LSV2_ERROR_T_ER_NO_NEXT_ERROR: 'Kein weiterer Fehler erhältlich',
            LSV2_ERROR_T_ER_ACCESS_TIMEOUT: 'Wartezeit beim Abholen von Daten abgelaufen',
            LSV2_ERROR_T_ER_NO_WRITE_ACCESS: 'kein Schreibzugriff (Preset: gelockte Zeilen)',
            LSV2_ERROR_T_ER_STIB: 'DNC Betrieb kann nicht aufgenommen werden, da Abarbeiten noch aktiv (STIB: Steuerung in Betrieb)',
            LSV2_ERROR_T_ER_REF_NECESSARY: 'Vor DNC Betrieb muß noch Reference gefahren werden',
            LSV2_ERROR_T_ER_PLC_BUF_FULL: 'PLC Puffer ist voll',
            LSV2_ERROR_T_ER_NOT_FOUND: 'Angeforderte Information nicht verfügbar (TableLine)',
            LSV2_ERROR_T_ER_WRONG_FILE: 'Falscher Dateityp (Versionsinfo in 1. Zeile defekt)',
            LSV2_ERROR_T_ER_NO_MATCH: 'Zu ersetzender PLC Binärcode stimmt nicht mit dem Binärcode auf der Steuerung überein (PLC Debug)',
            LSV2_ERROR_T_ER_TOO_MANY_TPTS: 'Zu viele Trace-Punkte',
            LSV2_ERROR_T_ER_NOT_ACTIVATED: 'Datei kann nicht aktiviert werden',
            LSV2_ERROR_T_ER_DSP_CHANNEL: 'Angegebener DSP Kanal nicht vorhanden',
            LSV2_ERROR_T_ER_DSP_PARA: 'Die gewünschten Daten können nicht gesendet werden',
            LSV2_ERROR_T_ER_OUT_OF_RANGE: 'Parameter ausserhalb des gültigen Bereichs',
            LSV2_ERROR_T_ER_INVALID_AXIS: 'gewählte Achsen ungültig',
            LSV2_ERROR_T_ER_STREAMING_ACTIVE: 'Achs-Streaming bereits aktiv',
            LSV2_ERROR_T_ER_NO_STREAMING_ACTIVE: 'Achs-Streaming nicht aktiv',
            LSV2_ERROR_T_ER_TO_MANY_OPEN_TCP: 'Zu viele TCP Ports auf Steuerung geöffnet',
            LSV2_ERROR_T_ER_NO_FREE_HANDLE: 'Kein freies (LSV-2) Handle',
            LSV2_ERROR_T_ER_PLCMEMREMA_CLEAR: 'Remanenter PLC Speicher wurde gelöscht',
            LSV2_ERROR_T_ER_OSZI_CHSEL: 'Kanal-Auswahl für Remote-Oszilloskop fehlerhaft',
            LSV2_ERROR_LSV2_BUSY: 'Telegrammübertragung noch aktiv (Backgroundtransfer)',
            LSV2_ERROR_LSV2_X_BUSY: 'letztes X_PC Telegram noch nicht quittiert',
            LSV2_ERROR_LSV2_NOCONNECT: 'Keine Verbindung',
            LSV2_ERROR_LSV2_BAD_BACKUP_FILE: 'Format der Backupdatei fehlerhaft',
            LSV2_ERROR_LSV2_RESTORE_NOT_FOUND: 'Wiederherzustellende Datei in Backup nicht gefunden',
            LSV2_ERROR_LSV2_DLL_NOT_INSTALLED: 'ASCII-Binär Konverter DLL nicht installiert ',
            LSV2_ERROR_LSV2_BAD_CONVERT_DLL: 'ACII-Binär Konverter DLL nicht gefunden oder fehlerhaft',
            LSV2_ERROR_LSV2_BAD_BACKUP_LIST: 'Backup-Listdatei fehlerhaft',
            LSV2_ERROR_LSV2_UNKNOWN_ERROR: 'Nicht genauer spezifizierter Fehler',
            LSV2_ERROR_T_BD_NO_NEW_FILE: 'Datei kann nicht geöffnet werden',
            LSV2_ERROR_T_BD_NO_FREE_SPACE: 'nicht genügend Platz für Datei',
            LSV2_ERROR_T_BD_FILE_NOT_ALLOWED: 'Programm und Dateiname stimmen nicht überein',
            LSV2_ERROR_T_BD_BAD_FORMAT: 'kein LF oder T_FD gesendet',
            LSV2_ERROR_T_BD_BAD_BLOCK: 'Fehler in Programmzeile (kann nicht binär gewandelt werden)',
            LSV2_ERROR_T_BD_END_PGM: 'Programmende bereits erreicht',
            LSV2_ERROR_T_BD_ANZ: 'Fehler bei Befehlsabarbeitung in der Anzeigetask',
            LSV2_ERROR_T_BD_WIN_NOT_DEFINED: 'Window noch gar nicht definiert',
            LSV2_ERROR_T_BD_WIN_CHANGED: 'Window hat sich in Zwischenzeit geändert',
            LSV2_ERROR_T_BD_DNC_WAIT: 'DNC-Puffer voll; Fileübertragung wird unterbrochen',
            LSV2_ERROR_T_BD_CANCELLED: 'Übertragung vom Benutzer abgebrochen',
            LSV2_ERROR_T_BD_OSZI_OVERRUN: 'Datenüberlauf (Baudrate zu niedrig)',
            LSV2_ERROR_T_BD_FD: 'Blockübertragung beendet (eigentlich kein Fehler)',
            LSV2_ERROR_T_USER_ERROR: 'Fehlernummer, wenn ein Fehlertelegramm der Fehlerkasse 2 ( benutzerdefinierter Klarschriftfehler) empfangen wurde'}.get(error_code, 'Unknown Error code')
    else:
        return {LSV2_ERROR_T_ER_BAD_FORMAT: 'format error in telegram',
            LSV2_ERROR_T_ER_UNEXPECTED_TELE: 'telegram not supported by protocol',
            LSV2_ERROR_T_ER_UNKNOWN_TELE: 'unknown telegram type',
            LSV2_ERROR_T_ER_NO_PRIV: 'no privilege for execution',
            LSV2_ERROR_T_ER_WRONG_PARA: 'wrong parameter',
            LSV2_ERROR_T_ER_BREAK: 'stopped by user',
            LSV2_ERROR_T_ER_BAD_KEY: 'bad key number for login',
            LSV2_ERROR_T_ER_BAD_FNAME: 'bad file or path name',
            LSV2_ERROR_T_ER_NO_FILE: 'file does not exist',
            LSV2_ERROR_T_ER_OPEN_FILE: 'could not open file',
            LSV2_ERROR_T_ER_FILE_EXISTS: 'file already exists',
            LSV2_ERROR_T_ER_BAD_FILE: 'file type unknown or not allowed',
            LSV2_ERROR_T_ER_NO_DELETE: 'could not delete file',
            LSV2_ERROR_T_ER_NO_NEW_FILE: 'could not create file',
            LSV2_ERROR_T_ER_NO_CHANGE_ATT: 'file is read only',
            LSV2_ERROR_T_ER_BAD_EMULATEKEY: 'bad key emulation',
            LSV2_ERROR_T_ER_NO_MP: 'machine parameter wrong or not supported',
            LSV2_ERROR_T_ER_NO_WIN: 'wrong window or screen number',
            LSV2_ERROR_T_ER_WIN_NOT_AKTIV: 'window not active',
            LSV2_ERROR_T_ER_ANZ: 'error while execution the view task',
            LSV2_ERROR_T_ER_FONT_NOT_DEFINED: 'font not defined',
            LSV2_ERROR_T_ER_FILE_ACCESS: 'error during file access',
            LSV2_ERROR_T_ER_WRONG_DNC_STATUS: 'wrong telegram for dnc state',
            LSV2_ERROR_T_ER_CHANGE_PATH: 'could not change directory',
            LSV2_ERROR_T_ER_NO_RENAME: 'could not rename file',
            LSV2_ERROR_T_ER_NO_LOGIN: 'login not possible',
            LSV2_ERROR_T_ER_BAD_PARAMETER: 'bad parameter in telegram',
            LSV2_ERROR_T_ER_BAD_NUMBER_FORMAT: 'bad number format',
            LSV2_ERROR_T_ER_BAD_MEMADR: 'bad memory address',
            LSV2_ERROR_T_ER_NO_FREE_SPACE: 'not enough free space',
            LSV2_ERROR_T_ER_DEL_DIR: 'could not delete directory',
            LSV2_ERROR_T_ER_NO_DIR: 'directory does not exist',
            LSV2_ERROR_T_ER_OPERATING_MODE: 'wron perating mode',
            LSV2_ERROR_T_ER_NO_NEXT_ERROR: 'no next error availible',
            LSV2_ERROR_T_ER_ACCESS_TIMEOUT: 'timeout while waiting for data',
            LSV2_ERROR_T_ER_NO_WRITE_ACCESS: 'no write access',
            LSV2_ERROR_T_ER_STIB: 'could not start DNC mode while machine is active',
            LSV2_ERROR_T_ER_REF_NECESSARY: 'could not start DNC mode while axes are not referenced',
            LSV2_ERROR_T_ER_PLC_BUF_FULL: 'PLC buffer full',
            LSV2_ERROR_T_ER_NOT_FOUND: 'information not found',
            LSV2_ERROR_T_ER_WRONG_FILE: 'wrong file type or format',
            LSV2_ERROR_T_ER_NO_MATCH: 'PLC binary code does not macht control',
            LSV2_ERROR_T_ER_TOO_MANY_TPTS: 'too many trace points',
            LSV2_ERROR_T_ER_NOT_ACTIVATED: 'could not activate file',
            LSV2_ERROR_T_ER_DSP_CHANNEL: 'DSP channel not availible',
            LSV2_ERROR_T_ER_DSP_PARA: 'could not read requested DSP data',
            LSV2_ERROR_T_ER_OUT_OF_RANGE: 'parameter out of range',
            LSV2_ERROR_T_ER_INVALID_AXIS: 'invalid axis',
            LSV2_ERROR_T_ER_STREAMING_ACTIVE: 'axis streaming already active',
            LSV2_ERROR_T_ER_NO_STREAMING_ACTIVE: 'no axis streaming active',
            LSV2_ERROR_T_ER_TO_MANY_OPEN_TCP: 'to many connections',
            LSV2_ERROR_T_ER_NO_FREE_HANDLE: 'no free LSV2 handle',
            LSV2_ERROR_T_ER_PLCMEMREMA_CLEAR: 'remanten PLC memory was cleared',
            LSV2_ERROR_T_ER_OSZI_CHSEL: 'chanel selection for remote scope incorrect',
            LSV2_ERROR_LSV2_BUSY: 'transmisson busy',
            LSV2_ERROR_LSV2_X_BUSY: 'last X_PC telegram was not acknowledged',
            LSV2_ERROR_LSV2_NOCONNECT: 'no connection',
            LSV2_ERROR_LSV2_BAD_BACKUP_FILE: 'backup file corrupt',
            LSV2_ERROR_LSV2_RESTORE_NOT_FOUND: 'file not fould in backup',
            LSV2_ERROR_LSV2_DLL_NOT_INSTALLED: 'ASCII-binary converter dll not installed',
            LSV2_ERROR_LSV2_BAD_CONVERT_DLL: 'ACII-binary converter dll not found or corrupt',
            LSV2_ERROR_LSV2_BAD_BACKUP_LIST: 'backup list file corrupt',
            LSV2_ERROR_LSV2_UNKNOWN_ERROR: 'unknown error',
            LSV2_ERROR_T_BD_NO_NEW_FILE: 'could not create new file',
            LSV2_ERROR_T_BD_NO_FREE_SPACE: 'nor enough free memory for file',
            LSV2_ERROR_T_BD_FILE_NOT_ALLOWED: 'file not allowed',
            LSV2_ERROR_T_BD_BAD_FORMAT: 'no LF oder T_FD sent',
            LSV2_ERROR_T_BD_BAD_BLOCK: 'error in program block',
            LSV2_ERROR_T_BD_END_PGM: 'end of program already reached',
            LSV2_ERROR_T_BD_ANZ: 'error in execution of display task',
            LSV2_ERROR_T_BD_WIN_NOT_DEFINED: 'wondow not defined',
            LSV2_ERROR_T_BD_WIN_CHANGED: 'window has changed',
            LSV2_ERROR_T_BD_DNC_WAIT: 'DNC-buffer full, file transfer interrupted',
            LSV2_ERROR_T_BD_CANCELLED: 'transfer canceled by user',
            LSV2_ERROR_T_BD_OSZI_OVERRUN: 'buffer overrund, boude rate to low',
            LSV2_ERROR_T_BD_FD: 'block transfer finished successfuly',
            LSV2_ERROR_T_USER_ERROR: 'error of type 2 with error message'}.get(error_code, 'Unknown Error code')
