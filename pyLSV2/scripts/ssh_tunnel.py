#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" this is a demo script to show how to use lsv2 via an sshtunnel and paramiko
For this to work you have to:
1. enable ssh connections on the control
2. create a ssh key pair on your computer
3. add the private key to one of the user accounts on the control (default is 'user')
4. make sure ssh is allowed through the firewall on the control
5. install the python library 'sshtunnel'
6. edit this file and set address, user name and path to the key file
"""
import logging
from sshtunnel import SSHTunnelForwarder
import pyLSV2

logging.basicConfig(level=logging.INFO)


def main():
    address = "192.168.56.101"
    user_name = "user"
    private_key_file = "<path to private key file>"
    lsv2_port = 19000

    print("Connecting to {:s}@{:s}:{:d} via ssh tunnel".format(user_name, address, lsv2_port))
    ssh_forwarder = SSHTunnelForwarder(
        address,
        ssh_username=user_name,
        ssh_pkey=private_key_file,
        remote_bind_address=("127.0.0.1", lsv2_port),
    )
    ssh_forwarder.start()
    print("SSH tunnel established. local port is {}".format(ssh_forwarder.local_bind_port))

    print("Establish regular LSV2 connection via local port")

    con = pyLSV2.LSV2("127.0.0.1", port=ssh_forwarder.local_bind_port, timeout=5, safe_mode=False)
    con.connect()
    print("Connected to '{:s}' with NC Software '{:s}'".format(con.versions.control, con.versions.nc_sw))
    print("Close Connection")
    con.disconnect()

    print("Close SSH tunnel")
    ssh_forwarder.stop()


if __name__ == "__main__":
    main()
