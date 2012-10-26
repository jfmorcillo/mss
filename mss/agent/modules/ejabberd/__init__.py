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

import re
import logging

logger = logging.getLogger()

def get_config_info():
    return ('setup-ejabberd.sh', ['hostname', 'domain'])

def get_hostname(module):
    """
    Return the server hostname
    """
    return module.MM.get_option("hostname")

def get_domain(module):
    """
    Return the server domain
    """
    return module.MM.get_option("domain")

def get_current_config():
    configuration_file = open('/etc/ejabberd/ejabberd.cfg')
    configuration = configuration_file.read()
    configuration_file.close()

    domain = re.search('^{hosts, \["(.*)"\]}', configuration, re.M)
    if domain:
        domain = domain.group(1)
    else:
        domain = ""
    logger.debug("domain: %s", domain)

    return {'domain': domain}
