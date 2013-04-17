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
import ConfigParser
import logging
import logging.handlers
import os
import sys
from sqlalchemy.exc import OperationalError
from sqlalchemy import create_engine

from mss.agent.managers.module import ModuleManager
from mss.agent.lib.db import Base

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-d", "--debug", action="store_true", dest="debug",
                      default=False, help="Enable debug mode")
    parser.add_option("-c", "--config", action="store", dest="config",
                      default='/etc/mss/agent.ini', help="Agent configuration file")

    (options, args) = parser.parse_args()

    print "Using configuration %s" % options.config
    config = ConfigParser.ConfigParser();
    try:
        config.readfp(open(options.config))
    except IOError as e:
        print "Error while reading configuration at %s" % options.config
        print e
        sys.exit(1)
    try:
        host = config.get("agent", "host")
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        host = 'localhost'
    try:
        port = config.getint("agent", "port")
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        port = 8001
    try:
        log_file = config.get("agent", "log_file")
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        log_file = '/var/log/mss/mss-agent.log'
    try:
        db_file = config.get("agent", "db_file")
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        db_file = '/var/lib/mss/mss-agent.db'

    # Create all tables if needed
    try:
        engine = create_engine('sqlite:///%s' % db_file)
        Base.metadata.create_all(engine)
    except OperationalError as e:
        print "Failed to setup the database %s" % db_file
        print e
        sys.exit(1)

    # Setup logging
    if not os.path.exists(log_file):
        try:
            h = open(log_file, 'w+')
            h.write("")
        except:
            print "Can't write to log file %s" % log_file
            sys.exit(1)
        else:
            h.close()
            os.chmod(log_file, 0600)

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
    fh = logging.handlers.RotatingFileHandler(log_file, maxBytes=10485760, backupCount=5)
    fh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)

    # Run the XML-RPC server
    MM = ModuleManager(config_path=options.config)
    server = SimpleXMLRPCServer((host, port), allow_none=True, logRequests=False)
    server.register_instance(MM)

    try:
        print 'This is MSS XML-RPC agent'
        print 'Listening at %s:%s' % (host, port)
        print 'Use Control-C to exit'
        server.serve_forever()
    except KeyboardInterrupt:
        print 'Exiting'
