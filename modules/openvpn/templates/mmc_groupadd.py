#!/usr/bin/python

import ldap
from mmc.plugins.base import createGroup, changeGroupDescription
from optparse import OptionParser


def mmc_create_group(group, description):
    try:
        createGroup(group)
        changeGroupDescription(group, description)
    except ldap.ALREADY_EXISTS:
        pass


if __name__ == "__main__":
    # Get options
    parser = OptionParser()

    parser.add_option("-g", "--group", dest="group", help="Group to create")
    parser.add_option("-d", "--description", dest="description", help="The description of the group to create")

    (options, args) = parser.parse_args()

    # Check options
    if options.group:
        if options.description:
            mmc_create_group(options.group, options.description)
