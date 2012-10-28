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

import re

def get_config_info():
    return ("setup-system.sh", ['hostname', 'domain'])

def get_hostname(module):
    """
        Return the current hostname
    """
    from socket import gethostname
    return gethostname()

def get_domain(module):
    """
        Return the current domain
        If none, return example.com
    """
    from socket import getfqdn
    try:
        domain = '.'.join(getfqdn().split('.')[1:])
    except:
        pass
    if not domain:
        domain = "example.com"
    return domain

def valid_hostname(string):
    """ validate hostname """
    if not re.match('^[a-z]+$', string):
        return "Incorrect hostname."
    else:
        return None

def check_configured():
    return False
