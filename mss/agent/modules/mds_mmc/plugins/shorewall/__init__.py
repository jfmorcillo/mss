# -*- coding: utf-8; -*-
#
# (c) 2012 Mandriva, http://www.mandriva.com
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.
#

"""
MDS shorewall plugin for the MMC agent.
"""

import os

from mmc.core.version import scmRevision
from mmc.plugins.shorewall.io import ShorewallConf, ShorewallLine

VERSION = "2.4.3"
APIVERSION = "6:2:4"
REVISION = scmRevision("$Rev$")

def getVersion(): return VERSION
def getApiVersion(): return APIVERSION
def getRevision(): return REVISION

def activate():
    return True


class ShorewallZones(ShorewallConf):

    def __init__(self):
        ShorewallConf.__init__(self, '/etc/shorewall/zones',
                               r'^(?P<name>[\w\d]+)\s+(?P<type>[\w\d]+)')
        self.read()

    def get(self, type = ""):
        zones = []
        for line in self.file:
            if isinstance(line, ShorewallLine) and line[0].startswith(type):
                zones.append(line[0])
        return zones


class ShorewallRules(ShorewallConf):

    def __init__(self):
        ShorewallConf.__init__(self, '/etc/shorewall/rules',
                r'^(?P<action>[\w\d/]+)\s+(?P<src>[\w\d]+)\s+(?P<dst>[\w\d]+)\s*(?P<proto>[\w\d]*)\s*(?P<dst_port>[:\w\d]*)')
        self.read()

    def add(self, action, src, dst, proto = "", dst_port = ""):
        action = action.split('/')
        if len(action) == 2:
            if not os.path.exists(os.path.join('/usr', 'share', 'shorewall', 'macro.%s' % action[0])) and \
               not os.path.exists(os.path.join('/etc', 'shorewall', 'macro.%s' % action[0])):
                raise ShorewallMacroDoesNotExists("Macro %s does not exists" % action[0])
        action = "/".join(action)
        self.add_line([action, src, dst, proto, dst_port])

class ShorewallMacroDoesNotExists(Exception):
    pass

# XML-RPC methods
def get_zones(type = ""):
    return ShorewallZones().get(type)

def add_rule(action, src, dst, proto = "", dst_port = ""):
    return ShorewallRules().add(action, src, dst, proto, dst_port)
