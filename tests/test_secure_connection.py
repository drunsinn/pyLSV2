#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests for lsv2 over ssh tunnel"""

try:
    import importlib.resources as importlib_resources
except (ImportError, AttributeError):
    import importlib_resources

import pytest
from sshtunnel import SSHTunnelForwarder, BaseSSHTunnelForwarderError

import pyLSV2
from . import test_files


@pytest.mark.skip(reason="no way of currently testing this")
def test_ssh_tunnel(address: str, timeout: float, port: int):
    """test if establishing a connection via ssh tunnel

    To create the ssh key pair for this test, run the following command in the base directory of this project:

    ```ssh-keygen -C "user@pyLSV2" -f pyLSV2_test -N "pyLSV2" -f ./tests/test_files/pyLSV2_test```

    After that, copy the public key (pyLSV2_test.pub) to the control and use the user settings to add the public key to the authorized keys of the user.
    """
    files = importlib_resources.files(test_files)
    priv_key = files.joinpath("pyLSV2_test")

    ssh_forwarder = SSHTunnelForwarder(
        ssh_address_or_host=address,
        ssh_username="user",
        ssh_password="pyLSV2",
        ssh_pkey=str(priv_key),
        remote_bind_address=("127.0.0.1", port),
    )

    try:
        ssh_forwarder.start()
    except BaseSSHTunnelForwarderError as e:
        pytest.fail("Unexpected ssh error: %s" % e)

    assert ssh_forwarder.is_active is True
    assert ssh_forwarder.local_bind_port > 0

    con = pyLSV2.LSV2("127.0.0.1", port=ssh_forwarder.local_bind_port, timeout=timeout, safe_mode=False)
    con.connect()
    assert con.login(login=pyLSV2.Login.INSPECT) is True

    assert isinstance(con.versions.nc_sw_base, int)
    assert isinstance(con.versions.nc_sw_type, int)

    con.disconnect()

    ssh_forwarder.stop()
