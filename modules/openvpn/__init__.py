# -*- coding: UTF-8 -*-
#
# (c) 2012 Mandriva, http://www.mandriva.com/
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
import netifaces
import re
import logging

from mss.agent.managers.translation import TranslationManager
from mss.agent.lib.utils import MANAGED_INTERFACE_NAMES

_ = TranslationManager().translate


def get_config_info():
    args = ["openvpn_country", "openvpn_province", "openvpn_city",
            "openvpn_org", "openvpn_email", "openvpn_networks", "interface"]
    return ('setup-openvpn.sh', args)


def get_interface_config(config):
    """
    Dynamic configuration for ethernet interfaces
    """
    CONFIG_DIR = "/etc/sysconfig/network-scripts"
    ifaces = []
    for interface in netifaces.interfaces():
        if interface.startswith(MANAGED_INTERFACE_NAMES):
            if_file = os.path.join(CONFIG_DIR, "ifcfg-%s" % interface)
            if_detail = netifaces.ifaddresses(interface)
            configured = os.path.exists(if_file) and netifaces.AF_INET in if_detail
            addr = ""
            if configured:
                s_iface = get_shorewall_interface(interface)
                addr = if_detail[netifaces.AF_INET][0]['addr']
                ifaces.append({'name': s_iface + ' (' + interface + ':' + str(addr) + ')',
                               'value': s_iface[0:3] + ' ' + str(addr)})

    config.append({'slug': 'openvpn',
                   'name': 'interface',
                   'label': _('VPN interface', 'openvpn'),
                   'help': _('The network interface where the VPN server will listen. It must be accessible by your VPN clients.',
                             'openvpn'),
                   'type': 'options',
                   'options': ifaces})

    return config


def get_shorewall_interface(iface):
    ''' Search for the Shorewall interface corresponding to the given ethX'''
    with open('/etc/shorewall/interfaces', 'r') as shorewall_interfaces:
        for line in shorewall_interfaces:
            m = re.search('(\w+) ' + iface, line)
            logging.debug(m)
            if m:
                return m.group(1)
