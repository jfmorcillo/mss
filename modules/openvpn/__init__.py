# -*- coding: UTF-8 -*-
#
# (c) 2012-2014 Mandriva, http://www.mandriva.com/
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

import netifaces
from IPy import IP

from mmc.plugins.shorewall import get_zones_types, get_zones_interfaces

from mss.agent.managers.translation import TranslationManager
from mss.agent.lib.utils import MANAGED_INTERFACE_NAMES

_ = TranslationManager().translate


def get_config_info():
    args = ["listen", "vpn_network", "push_networks",
            "country", "province", "city", "org", "email"]
    return ('setup-openvpn.sh', args)


def get_listen_config(config):
    """
    Get list of external addresses for openvpn
    """
    external_zones = get_zones_types()[1]
    external_interfaces = get_zones_interfaces(external_zones)

    ifaces = []
    for interface in netifaces.interfaces():
        if interface.startswith(MANAGED_INTERFACE_NAMES):
            for external_interface in external_interfaces:
                # tuple of ('zone', 'interface', 'options')
                if external_interface[1] == interface:
                    detail = netifaces.ifaddresses(interface)
                    addr = detail[netifaces.AF_INET][0]['addr']
                    ifaces.append({'name': '%s (%s)' % (addr, external_interface[0]),
                                   'value': "%s:%s" % (addr, external_interface[0])})

    config.append({'slug': 'openvpn',
                   'name': 'listen',
                   'required': 'yes',
                   'label': _('Listen address', 'openvpn'),
                   'help': _('The IP address where the VPN server will listen. It must be accessible by your VPN clients.',
                             'openvpn'),
                   'type': 'options',
                   'options': ifaces})

    return config


def get_push_networks_config(config):
    """
    Get list of internal networks to push to VPN clients
    """
    internal_zones = get_zones_types()[0]
    internal_interfaces = get_zones_interfaces(internal_zones)

    networks = []
    for interface in netifaces.interfaces():
        if interface.startswith(MANAGED_INTERFACE_NAMES):
            for internal_interface in internal_interfaces:
                if internal_interface[1] == interface:
                    detail = netifaces.ifaddresses(interface)
                    addr = detail[netifaces.AF_INET][0]['addr']
                    netmask = detail[netifaces.AF_INET][0]['netmask']
                    network = IP(addr).make_net(netmask)
                    networks.append([str(network.net()), str(network.netmask())])

    config.append({'slug': 'openvpn',
                   'name': 'push_networks',
                   'label': _('Shared networks', 'openvpn'),
                   'help': _('The list of internal networks that will be accessible to VPN clients.',
                             'openvpn'),
                   'type': 'network',
                   'format': 'long',
                   'multi': 'yes',
                   'default': networks})

    return config
