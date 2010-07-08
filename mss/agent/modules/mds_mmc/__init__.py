import re
import os
from mss.agent.utils import getINIoption

def get_config_info():
    return ("setup-mmc.sh", ['mdsdomain', 'mdspasswd', 'mdsppolicy'])

def get_current_config():

    ini='/etc/mmc/plugins/base.ini'
    if os.path.exists(ini):
        mdsdomain = getINIoption('ldap', 'baseDN', ini)
        mdsdomain = re.sub('^dc=', '', mdsdomain)
        mdsdomain = re.sub(',[\s]*dc=', '.', mdsdomain)
        if getINIoption('main', 'disable', '/etc/mmc/plugins/ppolicy.ini') == "0":
            mdsppolicy = "on"
        else:
            mdsppolicy = "off"
        return {'mdsdomain': mdsdomain, "mdsppolicy": mdsppolicy}
    else:
        return {}
