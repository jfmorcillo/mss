#!/usr/bin/python

import pam

print pam.authenticate('root', 'mandriva', service='passwd')
