#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
from SimpleXMLRPCServer import SimpleXMLRPCServer
from module import ModuleManager
from process import ExecManager
from translation import TranslationManager
from daemon import Daemon

class MSS(Daemon):
    def run(self):
        EM = ExecManager()
        TM = TranslationManager()
        MM = ModuleManager(EM, TM)
        server = SimpleXMLRPCServer(("localhost", 7000), allow_none=True,
            logRequests=False)
        server.register_instance(MM)
        server.serve_forever()

if __name__ == "__main__":
    daemon = MSS('/var/run/mss.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "Usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
