#!/usr/bin/python
# -*- coding: UTF-8 -*-

import xmlrpclib
import time


s = xmlrpclib.ServerProxy('http://localhost:7000')

#s.installModules(["openldap"])
#while 1:
#    print s.getState()
#    time.sleep(1)

#print state
#print code
#print output

modules = s.get_modules(['mds-mmc'])
print modules

#s.preInstallModules(["openldap"])
#s.getMedias(["openldap"])
