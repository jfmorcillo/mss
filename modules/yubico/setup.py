#!/usr/bin/env python
# Copyright Mandriva 2012 all rights reserved

import sys
import os
import shutil

sys.path.append('./')
import functions

print("test")
print(sys.argv[1:])

config = functions.MSSConfig()

yubikey = functions.ConfigFile('config/yubikey.ini')
yubikey.copy('/etc/yubico/yubikey.ini')

functions.LDAPSchema('config/yubikey.schema').add_schema()



print("END OF SETUP")
exit(-1)

