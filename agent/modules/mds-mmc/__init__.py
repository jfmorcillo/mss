#!/usr/bin/python
import re
import os

def get_config_info():
    return ("setup-mmc.sh", ['mdsdomain', 'mdspasswd'])

def get_current_config():
    if os.path.exists('/etc/mmc/plugins/base.ini'):
        h = open('/etc/mmc/plugins/base.ini')
        f = h.read()
        h.close()

        mdsdomain = re.search('^baseDN = (.*)$', f, re.MULTILINE)
        if mdsdomain:
            mdsdomain = mdsdomain.group(1)
            mdsdomain = re.sub('^dc=', '', mdsdomain)
            mdsdomain = re.sub(',dc=', '.', mdsdomain)
        else:
            mdsdomain = ""
        mdspasswd = re.search('^password = (.*)$', f, re.MULTILINE)
        if mdspasswd:
            mdspasswd = mdspasswd.group(1)
        else:
            mdspasswd = ""
    
        return {'mdsdomain': mdsdomain, 'mdspasswd': mdspasswd}
    else:
        return {}
