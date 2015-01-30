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

import traceback
import sys
import ConfigParser
import re
import os
import netifaces
from IPy import IP


MANAGED_INTERFACE_NAMES = ('eth', 'br', 'ens', 'enp', 'eno')


def formatExceptionInfo(maxTBlevel=5):
    cla, exc, trbk = sys.exc_info()
    excName = cla.__name__
    try:
        excArgs = exc.__dict__["args"]
    except KeyError:
        excArgs = "<no args>"
    excTb = traceback.format_tb(trbk, maxTBlevel)
    return str(excName + " " + excArgs + " : \n" + excTb[0])


def getINIoption(section, option, ini):
    config = ConfigParser.SafeConfigParser()
    config.read(ini)
    return config.get(section, option)


def get_config_option(file, option):
    """
    Returns the option value of a config file formatted like:
    OPTION=value
    """
    if os.path.exists(file):
        with open(file) as f:
            string = f.read()
        expr = re.compile("\s*%s\s*=\s*(.*)" % option, re.M)
        match = expr.search(string)
        if match and match.group(1):
            return match.group(1).strip()
        else:
            return ""
    else:
        raise OSError("File not found")


def grep(search, file):
    if os.path.exists(file):
        with open(file) as f:
            string = f.read()
        expr = re.compile(search, re.M)
        if expr.search(string):
            return True
        else:
            return False
    else:
        return False


def ethernet_ifs():
    ifs = []
    for interface in netifaces.interfaces():
        if interface.startswith(MANAGED_INTERFACE_NAMES):
            if_detail = netifaces.ifaddresses(interface)
            # check if interface is configured
            if netifaces.AF_INET in if_detail:
                addr = if_detail[netifaces.AF_INET][0]['addr']
                netmask = if_detail[netifaces.AF_INET][0]['netmask']
                network = IP(addr).make_net(netmask).strNormal(0)
                ifs.append([interface, addr, network, netmask])

    return ifs


def get_domain():
    """
        Return the current domain
    """
    from socket import getfqdn
    try:
        domain = '.'.join(getfqdn().split('.')[1:])
    except:
        domain = _("", "system")
    return domain


class Singleton(type):

    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls.instance = None

    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)
        return cls.instance
