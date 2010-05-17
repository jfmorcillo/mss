#!/usr/bin/python

import re
from IPy import IP

def get_config_info():
    return ("setup-dns.sh", ["bind_networks", "bind_forwarders"])

def get_current_config():

    h = open('/var/lib/named/etc/mss_acls.conf')
    f = h.read()
    h.close()
    networks = re.findall('^([\d]{1}.*);$', f, re.MULTILINE)
    bind_networks = []
    for net in networks:
        tmp = IP(net).strNormal(2).split('/')
        if len(tmp) > 1:
            ip = tmp[0]
            mask = tmp[1]
            bind_networks.append((ip, mask))

    h = open('/var/lib/named/etc/mss_forwarders.conf')
    f = h.read()
    h.close()
    forwarders = re.findall('^([\d]{1}.*);$', f, re.MULTILINE)
    bind_forwarders = []
    for forwarder in forwarders:
            bind_forwarders.append(forwarder)

    return {'bind_networks': bind_networks, 'bind_forwarders': bind_forwarders}
