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
import sys
import traceback

from sqlalchemy.exc import OperationalError
from sqlalchemy import create_engine

from mss.agent.config import Config
from mss.agent.server import MSSXMLRPCRequestHandler
from mss.agent.lib.db import Base

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-d", "--debug", action="store_true", dest="debug",
                      default=False, help="Enable debug mode")
    parser.add_option("-c", "--config", action="store", dest="config",
                      default='/etc/mss/agent.ini', help="Agent configuration file")

    (options, args) = parser.parse_args()

    # read configuration
    Config(options.config)

    # Create all tables if needed
    try:
        engine = create_engine('sqlite:///%s' % Config().db_file)
        Base.metadata.create_all(engine)
    except OperationalError as e:
        print "Failed to setup the database %s" % Config().db_file
        print traceback.format_exc()
        sys.exit(1)

    # Setup logging
    if not os.path.exists(Config().log_file):
        try:
            h = open(Config().log_file, 'w+')
            h.write("")
        except:
            print "Can't write to log file %s" % Config().log_file
            print traceback.format_exc()
            sys.exit(1)
        else:
            h.close()
            os.chmod(Config().log_file, 0600)

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
    fh = logging.handlers.RotatingFileHandler(Config().log_file, maxBytes=10485760, backupCount=5)
    fh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)

    # Run the XML-RPC server
    server = SimpleXMLRPCServer((Config().host, Config().port),
                                requestHandler=MSSXMLRPCRequestHandler,
                                allow_none=True, logRequests=False)

    try:
        print 'This is MSS XML-RPC agent'
        print 'Listening at %s:%s' % (Config().host, Config().port)
        print 'Use Control-C to exit'
        server.serve_forever()
    except KeyboardInterrupt:
        print 'Exiting'
