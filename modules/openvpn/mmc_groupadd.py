#!/usr/bin/python

import chardet
import ldap
import argparse

from mmc.plugins.base import createGroup, changeGroupDescription


def mmc_create_group(group, description=None):
    try:
        createGroup(group)
        if description is not None:
            changeGroupDescription(group, description)
    except ldap.ALREADY_EXISTS:
        pass


if __name__ == "__main__":
    # Get options
    parser = argparse.ArgumentParser()

    parser.add_argument("group", help="Group name to create")
    parser.add_argument("-d", "--description", dest="description", default=None,
                        help="The description of the group to create")

    args = parser.parse_args()

    # Check options
    description = None
    if args.description:
        description = args.description.decode(chardet.detect(args.description)['encoding'])
    mmc_create_group(args.group, description)
