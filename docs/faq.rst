FAQ
===

Q: connection doesn't work an/or login with user MONITOR fails on iTNC 530
--------------------------------------------------------------------------
Check [inventcom.net](https://www.inventcom.net/s1/_pdf/Heidenhain_TNC_Machine_Data.pdf) for
some steps on how to check some common problems. 

For iTNC 530:
- open the MOD dialog and enable the external access by toggling the soft key "External access"
- restart control

For TNC 320, 620, 640
- open the MOD dialog
- navigate to Machine settings/External access
- enable the external access by toggling the soft key "External access"
- restart control

If the soft key "External access" is not visible you have to change some parameters that require
the PLC password:
- iTNC: uncommented the line "REMOTE.LOCKSOFTKEYVISIBLE = YES" in PLC:/oem.sys
- TNC 320, 620, 640: add the parameter "denyAllConnections" in "CfgAccessControl" and/or set the value to False
