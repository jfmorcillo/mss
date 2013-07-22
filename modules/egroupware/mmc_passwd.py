#!/usr/bin/python

import ldap
import logging
from mmc.plugins.base import createUser, addUserToGroup, existGroup, existUser, LdapUserGroupControl
from optparse import OptionParser

def mmc_change_password(login, password):
    if existUser(login):
        LdapUserGroupControl().changeUserPasswd(login, password);

if __name__ == "__main__":
    # Get options
    parser = OptionParser()
    
    parser.add_option("-l", "--login", dest="login", help="User login")
    parser.add_option("-p", "--password", dest="password", help="New user password")

    (options, args) = parser.parse_args()

    # Check options
    if options.login and options.password:
        mmc_change_password(options.login, options.password)
        logging.debug('password changed')
    else:
        logging.debug('password not changed')
        exit(-1)
