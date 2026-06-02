pyLSV2 package content
======================

pyLSV2 Base
-----------

.. automodule:: pyLSV2

.. automodule:: pyLSV2.client

.. autoclass:: pyLSV2.LSV2
    :members:

Serial Interface Variant
------------------------

The `LSV2` constructor supports selecting the communication backend using the ``ser_url``
keyword argument. The tests demonstrate example usages and accepted URL formats. Typical
examples are:

.. code-block:: python

    # Use an internal loopback implementation (used in tests)
    con = pyLSV2.LSV2(hostname="", ser_url="loopback")

    # Use socket-based connection to a remote emulator or proxy
    con = pyLSV2.LSV2(hostname="", port=19000, ser_url="socket://hostname:8888")

    # Use serial port
    con = pyLSV2.LSV2(hostname="", port=19000, ser_url="serial:///dev/ttyUSB0")

When ``ser_url`` indicates a socket connection the TCP backend is selected; the loopback
value is provided for local test use. When a direct serial/RS232 port is required the
implementation selects the RS232 backend (see :mod:`pyLSV2.low_level_com`). Refer to the
tests for concrete examples of how to instantiate the class for each backend.

Table reader
------------

.. autoclass:: pyLSV2.NCTable
    :members:

Dataclasses
-----------

.. autoclass:: pyLSV2.dat_cls.VersionInfo
    :members:

.. autoclass:: pyLSV2.dat_cls.SystemParameters
    :members:

.. autoclass:: pyLSV2.dat_cls.ToolInformation
    :members:

.. autoclass:: pyLSV2.dat_cls.OverrideState
    :members:

.. autoclass:: pyLSV2.dat_cls.NCErrorMessage
    :members:

.. autoclass:: pyLSV2.dat_cls.StackState
    :members:

.. autoclass:: pyLSV2.dat_cls.FileEntry
    :members:

.. autoclass:: pyLSV2.dat_cls.DirectoryEntry
    :members:

.. autoclass:: pyLSV2.dat_cls.DriveEntry
    :members:

.. autoclass:: pyLSV2.dat_cls.LSV2Error
    :members:

Constants
---------

.. automodule:: pyLSV2.const
    :members:
    
Additions
---------
    
.. automodule:: pyLSV2.misc
    :members:


Scope specific classes and functions
------------------------------------
.. autoclass:: pyLSV2.dat_cls.ScopeSignal
    :members:

.. autoclass:: pyLSV2.dat_cls.ScopeSignalData
    :members:

.. autoclass:: pyLSV2.dat_cls.ScopeReading
    :members:

.. automodule:: pyLSV2.misc_scope
    :members: