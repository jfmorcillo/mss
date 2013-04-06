# -*- coding: UTF-8 -*-
#
# (c) 2010 Mandriva, http://www.mandriva.com/
#
# This file is part of Mandriva Server Setup
#
# MSS is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MSS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MSS; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import os
import re
from mss.agent.lib.utils import getINIoption
from mss.agent.managers.translation import TranslationManager

_ = TranslationManager().translate

def get_config_info():
    return ("setup-smb.sh", ["smbdomain", "smbnetbios", "smbadmin", "smbpasswd", "fw_lan", "fw_wan"])

def get_netbios(module):
    from socket import gethostname
    return gethostname().upper()

def valid_netbios(string):
    """ validate netbios """
    if not re.match('^[A-Z]+[A-Z0-9]*$', string):
        return _("Incorrect netbios name (only uppercase characters and digits allowed).", "mds_smb")
    else:
        return None

def valid_domain(string):
    """ validate domain """
    if not re.match('^[A-Z]+[A-Z0-9]*$', string):
        return _("Incorrect SAMBA domain name (only uppercase characters and digits allowed).", "mds_smb")
    else:
        return None

def get_current_config(module):

    ini='/etc/samba/smb.conf'
    if os.path.exists(ini):
        smbdomain = getINIoption('global', 'workgroup', ini)
        smbnetbios = getINIoption('global', 'netbios name', ini)
        return {'smbdomain': smbdomain, 'smbnetbios': smbnetbios, 'smbadmin': ''}
    else:
        return {}
