#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# (c) 2010 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Mandriva Server Setup
#
# MSS is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MSS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MSS; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import sys
from SimpleXMLRPCServer import SimpleXMLRPCServer
from managers.module import ModuleManager
from managers.process import ProcessManager
from managers.translation import TranslationManager
from lib.auth import authenticate

PM = ProcessManager()
TM = TranslationManager()
MM = ModuleManager(PM, TM)

server = SimpleXMLRPCServer(("localhost", 8001), allow_none=True)
server.register_instance(MM)
server.register_function(authenticate)

try:
    print 'This is MSS XML-RPC agent'
    print 'Use Control-C to exit'
    server.serve_forever()
except KeyboardInterrupt:
    print 'Exiting'
