import os

def get_config_info():
    return ('setup-repo.sh', [])

def check_configured():
    return os.system("grep zentyal_samba4_local_rpms /etc/urpmi/urpmi.cfg") == 0
