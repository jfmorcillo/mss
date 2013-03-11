#!/usr/bin/python

from mmc.plugins.base import createGroup, changeGroupDescription
from mss.agent.managers.translation import TranslationManager


_ = TranslationManager().translate

groups = {
    "InternetMaster": _("Full access to Internet", "mds_proxy"),
    "InternetFiltered": _("Filtered access to Internet", "mds_proxy"),
}

for group, desc in groups.items():
    createGroup(group)
    changeGroupDescription(group, desc)
