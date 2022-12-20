#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Exception for pyLSV2"""


class LSV2StateException(Exception):
    """raised for unknown or inconsisten states"""

    pass


class LSV2DataException(Exception):
    """raised if recived data could not be parsed"""

    pass


class LSV2InputException(Exception):
    """raised if input data could not be parsed"""

    pass


class LSV2ProtocolException(Exception):
    """raised when an unexpected response is recived"""

    pass