# -*- coding: UTF-8 -*-
#
# (c) 2013 Mandriva, http://www.mandriva.com/
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

from mss.agent.lib.utils import grep
from mss.agent.managers.translation import TranslationManager

_ = TranslationManager().translate
CONFIG_DIR = "/etc/sysconfig/network-scripts"

def get_pulse2_interfaces():
    # Get Pulse2 interfaces / zones
    from mmc.plugins.shorewall import get_rules
    interfaces = {}
    # [('Pulse2Inventory/ACCEPT', 'lan0', 'fw', '', '')]
    for rule in get_rules("Pulse2Inventory/ACCEPT"):
        zone = rule[1]
        interfaces[zone.replace('lan', 'eth')] = zone
    return interfaces

def get_config_info():
    args = []
    interfaces = get_pulse2_interfaces()
    for interface, zone in interfaces.items():
        if_file = os.path.join(CONFIG_DIR, "ifcfg-%s" % interface)
        if_detail = netifaces.ifaddresses(interface)
        configured = os.path.exists(if_file) and netifaces.AF_INET in if_detail
        if configured:
            args.append(interface + "_name")
            args.append(interface + "_zone")
            args.append(interface + "_dhcp")
            args.append(interface + "_addr")
            args.append(interface + "_netmask")
    return ("setup-pulse2-imaging.sh", args)

def get_interfaces_config(config):
    interfaces = get_pulse2_interfaces()
    for interface, zone in interfaces.items():
        if_file = os.path.join(CONFIG_DIR, "ifcfg-%s" % interface)
        if_detail = netifaces.ifaddresses(interface)
        configured = os.path.exists(if_file) and netifaces.AF_INET in if_detail
        if configured:
            addr = if_detail[netifaces.AF_INET][0]['addr']
            netmask = if_detail[netifaces.AF_INET][0]['netmask']
            network = IP('%s/%s' % (addr, netmask), make_net=True)
            config.append({'slug': 'pulse2_imaging', 'name': interface + '_name',
                           'type': 'text', 'hidden': 'yes', 'default': interface})
            config.append({'slug': 'pulse2_imaging', 'name': interface + '_zone',
                           'type': 'text', 'hidden': 'yes', 'default': zone})

            if grep("BOOTPROTO=dhcp", if_file):
                # Don't configure the DHCP since the interface is not static
                config.append({'slug': 'pulse2_imaging',
                               'name': interface + '_dhcp',
                               'type': 'text', 'hidden': 'yes', 'default': 'off'})
            else:
                ## configure DHCP
                config.append({'slug': 'pulse2_imaging',
                               'name': interface + '_dhcp',
                               'default': 'on',
                               'label': _("Configure a DHCP subnet on %s to handle Pulse2 imaging clients" % network, "pulse2_imaging"),
                               'help': _("Will create or update the DHCP subnet on the interface %s to handle PXE requests of Pulse2 imaging clients in the %s network. Uncheck if you want to use an external DHCP server for this network." % (interface, network), "pulse2_imaging"),
                               'type': 'check'})

            config.append({'slug': 'pulse2_imaging',
                           'name': interface + '_addr',
                           'type': 'text', 'hidden': 'yes',
                           'default': addr})
            config.append({'slug': 'pulse2_imaging',
                           'name': interface + '_netmask',
                           'type': 'text', 'hidden': 'yes',
                           'default': netmask})
    return config
