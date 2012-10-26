#!/usr/bin/python

from mmc.plugins.base import createGroup, changeGroupDescription

groups = {
    "Internet Master": "Free access to Internet and downloads",
    "Internet Filtered": "Filtered access to Internet and downloads",
    "Internet Time": "Access to Internet in specific hours"
}

for group, desc in groups.items():
    createGroup(group)
    changeGroupDescription(group, desc)
