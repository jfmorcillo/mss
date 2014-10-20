# -*- coding: UTF-8 -*-
#
# (c) 2014 Mandriva, http://www.mandriva.com/
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

from mss.agent.lib.utils import grep, MANAGED_INTERFACE_NAMES
from mss.agent.managers.translation import TranslationManager

_ = TranslationManager().translate


def get_interfaces():
    CONFIG_DIR = "/etc/sysconfig/network-scripts"
    for interface in netifaces.interfaces():
        if interface.startswith(MANAGED_INTERFACE_NAMES):
            if_file = os.path.join(CONFIG_DIR, "ifcfg-%s" % interface)
            if_detail = netifaces.ifaddresses(interface)
            configured = os.path.exists(if_file) and netifaces.AF_INET in if_detail
            if configured:
                if grep("BOOTPROTO=dhcp", if_file):
                    method = "dhcp"
                else:
                    method = "static"
                addr = if_detail[netifaces.AF_INET][0]['addr']
                yield (interface, addr, method)


def get_config_info():
    args = ['admin_password', 'pool_location']
    for interface, addr, method in get_interfaces():
        args.append(interface + '_name')
        args.append(interface + '_checked')
    args.append('fw_lan')
    args.append('fw_wan')
    return ('setup-libvirt.sh', args)


def get_bridge_config(config):
    """
    Bridge current interfaces
    """
    for interface, addr, method in get_interfaces():
        config.append({'slug': 'libvirt',
                       'name': interface + '_name',
                       'default': interface,
                       'type': 'text',
                       'hidden': 'yes'})
        config.append({'slug': 'libvirt',
                       'name': interface + '_checked',
                       'default': 'off',
                       'label': _('Create a bridge for interface %s (%s, %s)' % (interface, addr, method), 'libvirt'),
                       'help': _('You will be able to setup virtual machines on this network.', 'libvirt'),
                       'type': 'check'})
    return config
