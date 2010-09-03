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

# create the db for mss-agent
# upgrade mmc-wizard to mss-agent

import os
import ConfigParser
import sqlite3
from datetime import datetime

conf = '/var/lib/mmc-wizard/mds_config.ini'
bdd = '/var/lib/mss/mss-agent.db'
mapper = {
    'mds': 'mds_mmc',
    'samba': 'mds_smb',
    'mail': 'mds_mail',
    'webmail': 'mds_webmail',
    'dns': 'mds_dns',
    'dhcp': 'mds_dhcp',
    'cups': 'mds_cups',
}

# create db
if not os.path.exists(bdd):
    print "Setup mss agent database...",
    conn = sqlite3.connect(bdd)
    c = conn.cursor()
    c.execute('create table module(name varchar(50), configured varchar(50));')
    conn.commit()
    c.close()
    print "done."
else:
    conn = sqlite3.connect(bdd)

# upgrade
if os.path.exists(conf):
    print "Upgrading mmc-wizard..."
    config = ConfigParser.ConfigParser()
    config.read(conf)
    for old_module, new_module in mapper.items():
        try:
            print "Check "+old_module+"...",
            if config.get("configured", old_module) == '1':
                c = conn.cursor()
                c.execute('insert into module values (?,?)', (new_module, datetime.now()))
                conn.commit()
                c.close()
                print "is configured."
            else:
                print "not configured."
        except ConfigParser.NoOptionError:
            print "not configured."
    print "Done."
