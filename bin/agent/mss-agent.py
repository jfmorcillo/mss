#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import os
import sqlite3
from SimpleXMLRPCServer import SimpleXMLRPCServer
from mss.agent.module import ModuleManager
from mss.agent.process import ExecManager
from mss.agent.translation import TranslationManager
from mss.agent.daemon import Daemon
from mss.agent.auth import authenticate

class MSS(Daemon):
    def run(self):
        EM = ExecManager()
        TM = TranslationManager()
        MM = ModuleManager(EM, TM)
        server = SimpleXMLRPCServer(("localhost", 7000), allow_none=True,
            logRequests=False)
        server.register_instance(MM)
        server.register_function(authenticate)
        server.serve_forever()

if __name__ == "__main__":

    # create db first time
    if not os.path.exists('/var/lib/mss/mss-agent.db'):
        conn = sqlite3.connect('/var/lib/mss/mss-agent.db')
        c = conn.cursor()
        c.execute('create table module(name varchar(50), configured varchar(50));')
        conn.commit()
        c.close()

    daemon = MSS('/var/run/mss-agent.pid')
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
