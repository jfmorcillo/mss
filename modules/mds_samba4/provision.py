#!/usr/bin/env python

import sys
import logging
# Set up logging
root = logging.getLogger()
root.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

from twisted.internet import reactor
from mmc.plugins.samba4 import provisionSamba

def provision_ok(ret):
    if ret:
        print "Provision of Samba4 done."
    reactor.stop()

def provision_err(failure):
    print "Provision of Samba4 FAILED"
    print str(failure)
    reactor.stop()
    sys.exit(1)

d = provisionSamba(*sys.argv[1:])
d.addCallback(provision_ok)
d.addErrback(provision_err)
reactor.run()
