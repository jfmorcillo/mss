#!/usr/bin/python

import os
import re
from subprocess import Popen, PIPE
from IPy import IP

def get_config_info():
    return ('setup-mail.sh', ['smtpd_myhostname', 'smtpd_mynetworks', 'popimap_proto'])

def get_current_config():

    # get postfix config
    p = Popen(['/usr/sbin/postconf', '-h', 'myhostname'], stdout=PIPE)
    smtpd_myhostname = p.communicate()[0].strip()

    p = Popen(['/usr/sbin/postconf', '-h', 'mynetworks'], stdout=PIPE)
    networks = p.communicate()[0].strip().split(',')
    smtpd_mynetworks = []
    for net in networks:
        tmp = IP(net).strNormal(2).split('/')
        if len(tmp) > 1:
            ip = tmp[0]
            mask = tmp[1]
            smtpd_mynetworks.append((ip, mask))

    # get dovecot config
    h = open('/etc/dovecot.conf')
    f = h.read()
    h.close()

    popimap_proto = re.search('^protocols[\s]*=[\s]*(.*)$', f, re.MULTILINE)
    if popimap_proto:
        popimap_proto = popimap_proto.group(1).strip()
    else:
        popimap_proto = ""

    return {'smtpd_myhostname': smtpd_myhostname, 
        'smtpd_mynetworks': smtpd_mynetworks, 'popimap_proto': popimap_proto}
