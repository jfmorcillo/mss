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
import os
import subprocess

def get_config_info():
    return ("setup-kerberos.sh", ["realm", "dns_domain_name","kdc_host_name", "kdc_port", "kadmin_port", "kdc_key_passwd", 
    "dns_lookup_kdc", "dns_lookup_realm", "tgs_enctypes", "tkt_enctypes", "permitted_enctypes","allow_weak_enctypes", "clock_skew"])


def get_current_config(module):
    config = {}
    KRB_CONF = "/etc/krb5.conf"
    KRB_CONF_PARAMS = {
	"^\s*default_realm\s*=\s*(.*)" : ["realm"],
	"^\s*admin_server\s*=\s*([a-zA-Z0-9_]+)\.([a-zA-Z0-9_.]+):(\d+)" : ["kdc_host_name", "dns_domain_name", "kadmin_port"],
        "^\s*default_tgs_enctypes\s*=\s*(.*)" : ["tgs_enctypes"],
        "^\s*default_tkt_enctypes\s*=\s*(.*)" : ["tkt_enctypes"],
        "^\s*permitted_enctypes\s*=\s*(.*)" : ["permitted_enctypes"],
        "^\s*clockskew\s*=\s*(.*)" : ["clock_skew"],
        "^\s*allow_weak_crypto\s*=\s*(.*)" : ["allow_weak_enctypes"],
        "^\s*dns_lookup_kdc\s*=\s*(.*)" : ["dns_lookup_kdc"],
        "^\s*dns_lookup_realm\s*=\s*(.*)" : ["dns_lookup_realm"]
		      }
    KDC_CONF = "/etc/kerberos/krb5kdc/kdc.conf"
    KDC_CONF_PARAMS = { "^\s*kdc_ports\s*=\s*(\d+)" : ["kdc_port"]}

    config = get_config_from_file(KRB_CONF, KRB_CONF_PARAMS)
    config.update(get_config_from_file(KDC_CONF, KDC_CONF_PARAMS))

    for key in config.keys():
	if config[key] == "true":
	    config[key] = "on"
	elif config[key] == "false":
	    config[key] = "off"
    return config


def get_config_from_file(file, configMap):
    config = {}
    if os.path.exists(file):
	f = open(file)
	data = f.read()
	f.close()
	
	maxParamsCount = 0
	for regexp, values in configMap.items():
	    maxParamsCount += len(values)
	
	paramsCount = 0
	for line in data.split("\n"):
	    for regexp, values in configMap.items():
		matches = re.match(regexp,line)
		if matches:
		    groups = matches.groups()
		    for index in range(len(groups)):
			config[values[index]] = groups[index]
			paramsCount += 1
		    break
	    if (paramsCount == maxParamsCount):
		break
    return config

def get_default_domain_name():
    return subprocess.Popen(["dnsdomainname"], stdout=subprocess.PIPE).communicate()[0].strip()

def get_default_host_name():
    return subprocess.Popen(["hostname","-s"], stdout=subprocess.PIPE).communicate()[0].strip()

def get_default_realm():
    return get_default_domain_name().upper()

def check_realm(realm):
    if not re.match('^[A-Z0-9-\.]+\.[A-Z]{2,}$', realm):
        return "Incorrect realm."
    return None

def check_kdc_host_name(host_name):
    if not re.match('^[a-zA-Z0-9-]+$', host_name):
        return "Incorrect host name."
    return None

def check_port(port):
    if not re.match('^([0-5]?\d?\d?\d?\d|6[0-4]\d\d\d|65[0-4]\d\d|655[0-2]\d|6553[0-5])$', port):
	return "Incorrect port number."
    return None

def check_configured():
    checker = "%s/check_configured.sh" % os.path.dirname(os.path.abspath(__file__))
    code = subprocess.call([checker])
    return bool(code)
