#!/usr/bin/python

import ldap
import logging
from mmc.plugins.base import createUser, addUserToGroup, existGroup, existUser, LdapUserGroupControl
from optparse import OptionParser

if __name__ == "__main__":
    # Get options
    parser = OptionParser()
    
    parser.add_option("-l", "--login", dest="login", help="User login")
    parser.add_option("-p", "--password", dest="password", help="User password")

    (options, args) = parser.parse_args()

    # Check options
    if options.login and options.password:
        createUser(options.login, options.password,"","","");
        logging.debug('user created')
    else:
        logging.debug('user not created')
        exit(-1)
