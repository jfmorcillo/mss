#!/usr/bin/python

import os
from mss.agent.utils import getINIoption

def get_config_info():
    return ("setup-smb.sh", ["smbdomain", "smbnetbios", "smbadmin", "smbpasswd"])

def get_current_config():

    ini='/etc/samba/smb.conf'
    if os.path.exists(ini):
        smbdomain = getINIoption('global', 'workgroup', ini)
        smbnetbios = getINIoption('global', 'netbiosname', ini)    
        return {'smbdomain': smbdomain, 'smbnetbios': smbnetbios, 'smbadmin': ''}
    else:
        return {}
