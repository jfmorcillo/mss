import re
import os
from mss.agent.utils import getINIoption

def get_config_info():
    return ("setup-mmc.sh", ['mdsdomain', 'mdspasswd'])

def get_current_config():

    ini='/etc/mmc/plugins/base.ini'
    if os.path.exists(ini):
        mdsdomain = getINIoption('ldap', 'baseDN', ini)
        mdsdomain = re.sub('^dc=', '', mdsdomain)
        mdsdomain = re.sub(',dc=', '.', mdsdomain)
        mdspasswd = getINIoption('ldap', 'password', ini)    
        return {'mdsdomain': mdsdomain, 'mdspasswd': mdspasswd}
    else:
        return {}
