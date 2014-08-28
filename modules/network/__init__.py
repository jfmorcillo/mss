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

from mss.agent.lib.utils import grep, get_config_option
from mss.agent.managers.translation import TranslationManager

_ = TranslationManager().translate


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
    args = args + ["fw_mss_lan", "fw_ssh_lan", "fw_mss_wan", "fw_ssh_wan"]
    return ("setup-network.sh", args)


def get_interfaces_config(config):
    """
    Dynamic configuration for ethernet interfaces
    """
    CONFIG_DIR = "/etc/sysconfig/network-scripts"
    for interface in netifaces.interfaces():
        if interface.startswith("eth") or interface.startswith("br"):
            if_file = os.path.join(CONFIG_DIR, "ifcfg-%s" % interface)
            if_detail = netifaces.ifaddresses(interface)
            configured = os.path.exists(if_file) and netifaces.AF_INET in if_detail
            method = "none"
            addr = ""
            netmask = ""
            dns1 = ""
            dns2 = ""
            domain = ""
            gateway = ""
            type = ""
            with open('/etc/shorewall/interfaces') as h:
                for line in h.readlines():
                    if interface in line:
                        type = line.split()[0]
                        break
            if configured:
                if grep("BOOTPROTO=dhcp", if_file):
                    method = "dhcp"
                else:
                    method = "static"
                addr = if_detail[netifaces.AF_INET][0]['addr']
                netmask = if_detail[netifaces.AF_INET][0]['netmask']
                dns1 = get_config_option(if_file, "DNS1")
                dns2 = get_config_option(if_file, "DNS2")
                domain = get_config_option(if_file, "DOMAIN")
                gateway = get_config_option(if_file, "GATEWAY")

            config.append({'slug': 'network',
                           'type': 'subtitle', 'label': interface})
            config.append({'slug': 'network', 'name': interface + '_name',
                           'type': 'text', 'hidden': 'yes', 'default': interface})
            config.append({'slug': 'network',
                           'name': interface + '_type',
                           'show_if_unconfigured': 'yes',
                           'require': 'yes',
                           'default': type,
                           'label': _('Interface type', 'network'),
                           'help': _('Choose "External" if the interface is connected to the Internet. If the interface is connected to an internal network, choose "Internal"', 'network'),
                           'type': 'options',
                           'options': [
                               {'name': _('Internal network', 'network'), 'value': 'lan' + interface[-1]},
                               {'name': _('External network', 'network'), 'value': 'wan' + interface[-1]}
                           ]
                           })
            config.append({'slug': 'network',
                           'name': interface + '_method',
                           'default': method,
                           'require': 'yes',
                           'label': _('Configuration method', 'network'),
                           'type': 'options',
                           'options': [
                               {'name': _('No configuration', 'network'), 'value': 'none'},
                               {'name': _('DHCP configuration', 'network'), 'value': 'dhcp'},
                               {'name': _('Manual configuration', 'network'), 'value': 'static',
                                'toggle': [interface + '_addr', interface + '_netmask', interface + '_dns1',
                                           interface + '_dns2', interface + '_domain', interface + '_gateway']}
                           ]
                           })
            config.append({'slug': 'network',
                           'name': interface + '_addr',
                           'default': addr,
                           'label': _('IP Address', 'network'),
                           'type': 'text', 'validation': 'ip'})
            config.append({'slug': 'network',
                           'name': interface + '_netmask',
                           'default': netmask,
                           'label': _('Netmask', 'network'),
                           'type': 'text', 'validation': 'ip'})
            config.append({'slug': 'network',
                           'name': interface + '_dns1',
                           'default': dns1,
                           'label': _('First DNS server', 'network'),
                           'type': 'text', 'validation': 'ip'})
            config.append({'slug': 'network',
                           'name': interface + '_dns2',
                           'default': dns2,
                           'label': _('Second DNS server', 'network'),
                           'type': 'text', 'validation': 'ip'})
            config.append({'slug': 'network',
                           'name': interface + '_domain',
                           'default': domain,
                           'label': _('Domain search', 'network'),
                           'type': 'text', 'validation': 'fqdn'})
            config.append({'slug': 'network',
                           'name': interface + '_gateway',
                           'default': gateway,
                           'label': _('Gateway', 'network'),
                           'type': 'text', 'validation': 'ip'})

    config.append({'slug': 'network',
                   'type': 'subtitle', 'label': _('Firewall configuration', 'network')})
    config.append({'slug': 'network',
                   'name': 'fw_mss_lan',
                   'default': 'on',
                   'label': _('Allow access to Mandriva Server Setup from internal networks', 'network'),
                   'type': 'check'})
    config.append({'slug': 'network',
                   'name': 'fw_ssh_lan',
                   'default': 'on',
                   'label': _('Allow SSH access from internal networks', 'network'),
                   'type': 'check'})
    config.append({'slug': 'network',
                   'name': 'fw_mss_wan',
                   'default': 'off',
                   'label': _('Allow access to Mandriva Server Setup from external networks', 'network'),
                   'type': 'check'})
    config.append({'slug': 'network',
                   'name': 'fw_ssh_wan',
                   'default': 'on',
                   'label': _('Allow SSH access from external networks', 'network'),
                   'type': 'check'})

    return config
