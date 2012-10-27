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

import os
import re
from subprocess import Popen, PIPE
from IPy import IP

from mss.agent.lib.utils import ethernet_ifs 

def get_config_info():
    return ('setup-mail.sh', ['smtpd_myhostname', 'smtpd_mynetworks', 'popimap_proto'])

def get_current_config(module):

    # get postfix config
    p = Popen(['/usr/sbin/postconf', '-h', 'myhostname'], stdout=PIPE)
    smtpd_myhostname = p.communicate()[0].strip()

    p = Popen(['/usr/sbin/postconf', '-h', 'mynetworks'], stdout=PIPE)
    networks = p.communicate()[0].strip().split(',')
    smtpd_mynetworks = []
    for net in networks:
        tmp = IP(net).strNormal(2).split('/')
        if len(tmp) > 1:
            ip = tmp[0]
            mask = tmp[1]
            smtpd_mynetworks.append((ip, mask))

    # get dovecot config
    h = open('/etc/dovecot.conf')
    f = h.read()
    h.close()

    popimap_proto = re.search('^protocols[\s]*=[\s]*(.*)$', f, re.MULTILINE)
    if popimap_proto:
        popimap_proto = popimap_proto.group(1).strip()
    else:
        popimap_proto = ""

    return {'smtpd_myhostname': smtpd_myhostname, 
        'smtpd_mynetworks': smtpd_mynetworks, 'popimap_proto': popimap_proto}

def get_fqdn(module):
    """
    Return the server FQDN
    """

    hostname = module.MM.get_option("hostname")
    domain = module.MM.get_option("domain")

    return hostname + "." + domain

def get_networks(module):
    """
    Return networks of the local machine
    """

    networks = []
    for iface in ethernet_ifs():
        networks.append((iface[2], iface[3]))

    return networks
