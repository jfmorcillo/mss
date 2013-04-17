#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# (c) 2010-2012 Mandriva, http://www.mandriva.com/
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

from SimpleXMLRPCServer import SimpleXMLRPCServer
from optparse import OptionParser
import logging
import logging.handlers
import os

from mss.agent.managers.module import ModuleManager
from mss.agent.lib.db import Base, engine

if __name__ == "__main__":

    # Create all tables if needed
    Base.metadata.create_all(engine)

    parser = OptionParser()
    parser.add_option("-d", "--debug", action="store_true", dest="debug",
                      default=False, help="Enable debug mode")
    parser.add_option("-c", "--config", action="store", dest="config",
                      default='/etc/mss/agent.ini', help="Agent configuration file")

    (options, args) = parser.parse_args()

    # Setup logging
    LOG_FILENAME = '/var/log/mss/mss-agent.log'
    os.chmod(LOG_FILENAME, 0600)

    level = logging.ERROR
    format = '%(asctime)s - %(message)s'
    if options.debug:
        level = logging.DEBUG
        format = '%(asctime)s|%(name)s|%(levelname)s: %(message)s'

    logger = logging.getLogger()
    logger.setLevel(level)

    formatter = logging.Formatter(format)

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    fh = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=10485760, backupCount=5)
    fh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)

    # Run the XML-RPC server
    logger.debug("Using configuration %s" % options.config)
    MM = ModuleManager(config_path=options.config)

    server = SimpleXMLRPCServer(("localhost", 8001), allow_none=True, logRequests=False)
    server.register_instance(MM)

    try:
        print 'This is MSS XML-RPC agent'
        print 'Use Control-C to exit'
        server.serve_forever()
    except KeyboardInterrupt:
        print 'Exiting'
