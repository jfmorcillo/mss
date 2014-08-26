#!/usr/bin/python

import sys
from mss.agent.lib import pam

password = sys.argv[1]

result = pam.authenticate("root", password, service="passwd")
if result:
    print 0
    sys.exit(0)
print 1
sys.exit(1)
