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
from IPy import IP

from mss.agent.lib.utils import grep, get_config_option

def get_config_info():
    args = []
    for interface in netifaces.interfaces():
        if interface.startswith("eth"):
            args.append(interface + "_name")
            args.append(interface + "_type")
            args.append(interface + "_method")
            args.append(interface + "_addr")
            args.append(interface + "_netmask")
            args.append(interface + "_dns1")
            args.append(interface + "_dns2")
            args.append(interface + "_domain")
            args.append(interface + "_gateway")
    return ("setup-network.sh", args)

def get_interfaces_config(config):
    """
    Dynamic configuration for ethernet interfaces
    """
    CONFIG_DIR = "/etc/sysconfig/network-scripts"
    GATEWAY = "/etc/sysconfig/network"
    for interface in netifaces.interfaces():
        if interface.startswith("eth"):
            if_file = os.path.join(CONFIG_DIR, "ifcfg-%s" % interface)
            if_detail = netifaces.ifaddresses(interface)
            configured = os.path.exists(if_file) and netifaces.AF_INET in if_detail
            addr = ""
            netmask = ""
            dns1 = ""
            dns2 = ""
            domain = ""
            gateway = ""
            if configured:
                if grep(if_file, "BOOTPROTO=dhcp"):
                    method = "dhcp"
                else:
                    method = "static"
                addr = if_detail[netifaces.AF_INET][0]['addr']
                netmask = if_detail[netifaces.AF_INET][0]['netmask']
                dns1 = get_config_option(if_file, "DNS1")
                dns2 = get_config_option(if_file, "DNS2")
                domain = get_config_option(if_file, "DOMAIN")
                gateway = get_config_option(if_file, "GATEWAY")

                config.append({'id': 'network',
                               'type': 'subtitle', 'label': interface})
                config.append({'id': 'network', 'name': interface + '_name',
                               'type': 'text', 'hidden': 'yes', 'default': interface})
                config.append({'id': 'network',
                               'name': interface + '_type',
                               'require': 'yes',
                               'label': 'Interface type',
                               'type': 'options',
                               'options': [
                                   {'name': 'Internal network', 'value': 'lan' + interface[:-1]},
                                   {'name': 'External network', 'value': 'wan' + interface[:-1]}
                                ]
                               })
                config.append({'id': 'network',
                               'name': interface + '_method',
                               'default': method, 'require': 'yes',
                               'label': 'Configuration method',
                               'type': 'options',
                               'options': [
                                   {'name': 'DHCP configuration', 'value': 'dhcp'},
                                   {'name': 'Manual configuration', 'value': 'static',
                                    'toggle': [interface + '_addr', interface + '_netmask', interface + '_dns1',
                                               interface + '_dns2', interface + '_domain', interface + '_gateway']}
                                ]
                               })
                config.append({'id': 'network',
                               'name': interface + '_addr',
                               'default': addr,
                               'label': 'IP Address',
                               'type': 'text', 'validation': 'ip'})
                config.append({'id': 'network',
                               'name': interface + '_netmask',
                               'default': netmask,
                               'label': 'Netmask',
                               'type': 'text', 'validation': 'ip'})
                config.append({'id': 'network',
                               'name': interface + '_dns1',
                               'default': dns1,
                               'label': 'First DNS server',
                               'type': 'text', 'validation': 'ip'})
                config.append({'id': 'network',
                               'name': interface + '_dns2',
                               'default': dns2,
                               'label': 'Second DNS server',
                               'type': 'text', 'validation': 'ip'})
                config.append({'id': 'network',
                               'name': interface + '_domain',
                               'default': domain,
                               'label': 'Domain search',
                               'type': 'text', 'validation': 'fqdn'})
                config.append({'id': 'network',
                               'name': interface + '_gateway',
                               'default': gateway,
                               'label': 'Gateway',
                               'type': 'text', 'validation': 'ip'})
    return config

def check_configured():
    return False
