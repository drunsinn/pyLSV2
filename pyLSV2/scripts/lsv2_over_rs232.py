#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This script contains examples on how to use different functions of pyLSV2 via RS232
Not all functions are shown here
"""

import logging
import pyLSV2


def main():
    logging.basicConfig(level=logging.DEBUG)

    with pyLSV2.LSV2(hostname="", timeout=1, ser_url="socket://localhost:8888") as con:
        con.connect()
        con.disconnect()


if __name__ == "__main__":
    main()
