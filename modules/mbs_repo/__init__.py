
from mss.agent.lib.utils import grep

def get_config_info():
    return ('setup-repo.sh', [])

def check_configured():
    return grep('mirror.mandriva.com/mbs1/x86_64', '/etc/urpmi/urpmi.cfg')

