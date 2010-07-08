#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
from SimpleXMLRPCServer import SimpleXMLRPCServer
from module import ModuleManager
from process import ExecManager
from translation import TranslationManager
from auth import authenticate

EM = ExecManager()
TM = TranslationManager()
MM = ModuleManager(EM, TM)
server = SimpleXMLRPCServer(("localhost", 8001), allow_none=True)
server.register_instance(MM)
server.register_function(authenticate)
server.serve_forever()
