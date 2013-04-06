#!/usr/bin/python

import ldap
from mmc.plugins.base import createGroup, changeGroupDescription
from mss.agent.managers.translation import TranslationManager


_ = TranslationManager().translate

groups = {
    "InternetMaster": _("Full access to Internet", "squid"),
    "InternetFiltered": _("Filtered access to Internet", "squid"),
}

for group, desc in groups.items():
    try:
        createGroup(group)
        changeGroupDescription(group, desc)
    except ldap.ALREADY_EXISTS:
        pass
