#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
from SimpleXMLRPCServer import SimpleXMLRPCServer
from module import ModuleManager
from process import ExecManager
from translation import TranslationManager

EM = ExecManager()
TM = TranslationManager()
MM = ModuleManager(EM, TM)
server = SimpleXMLRPCServer(("localhost", 7000), allow_none=True,
    logRequests=False)
server.register_instance(MM)
server.serve_forever()
